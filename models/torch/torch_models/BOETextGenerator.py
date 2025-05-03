import os
import xml.etree.ElementTree as ET
from typing import List, Tuple
from datetime import datetime

import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    GPT2TokenizerFast,
    GPT2LMHeadModel,
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling,
    BartTokenizerFast,
    BartForConditionalGeneration
)
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import random

# -------------------------------
# Utility: List XML files by date range
# -------------------------------
def list_xml_files_in_range(
    base_dir: str,
    start_date: str,
    end_date: str,
    date_format: str = "%d/%m/%Y"
) -> List[str]:
    """
    Recorre el directorio base_dir que contiene subdirectorios por año y fecha (YYYY/YYYYMMDD/xml/*.xml)
    y devuelve la lista de rutas de archivos XML cuya fecha esté entre start_date y end_date (inclusive).

    Args:
        base_dir: ruta raíz, p.ej. 'backend/data/boe/diario'
        start_date: fecha inicio en formato 'DD/MM/YYYY'
        end_date: fecha fin en formato 'DD/MM/YYYY'
        date_format: formato de las fechas de entrada
        Tiene que devolver una ruta como 'backend/data/boe/diario/2023/20230101/xml/*.xml'

    Returns:
        Lista de rutas absolutas a archivos .xml dentro del rango.
    """
    # convertir fechas a objetos
    start = datetime.strptime(start_date, date_format)
    end = datetime.strptime(end_date, date_format)
    xml_paths = []
    # recorrer años entre los dos
    for year in os.listdir(base_dir):
        year_path = os.path.join(base_dir, year)
        if not os.path.isdir(year_path) or not year.isdigit():
            continue
        # cada subcarpeta de fecha YYYYMMDD
        for date_folder in os.listdir(year_path):
            date_path = os.path.join(year_path, date_folder)
            # formato carpeta debe ser YYYYMMDD
            try:
                folder_date = datetime.strptime(date_folder, "%Y%m%d")
            except ValueError:
                continue
            # comprobar rango
            if start <= folder_date <= end:
                xml_dir = os.path.join(date_path, 'xml')
                if os.path.isdir(xml_dir):
                    for fn in os.listdir(xml_dir):
                        if fn.endswith('.xml'):
                            xml_paths.append(os.path.join(xml_dir, fn))
    return sorted(xml_paths)

# -------------------------------
# 1) Generative Model (GPT-2)
# -------------------------------
class BOETextDataset(Dataset):
    def __init__(
        self,
        file_list: List[str],
        tokenizer: GPT2TokenizerFast,
        block_size: int = 512,
    ):
        self.tokenizer = tokenizer
        self.block_size = block_size
        self.examples = []
        # Procesar cada XML en file_list por separado
        for path in file_list:
            tree = ET.parse(path)
            root = tree.getroot()
            title = root.findtext('.//titulo') or ''
            paragraphs = [p.text for p in root.findall('.//texto//p') if p.text]
            body = "\n".join(paragraphs)
            doc = f"<TITULO> {title} </TITULO>\n<BODY> {body} </BODY>"
            # Tokenizar cada documento por separado y dividir en bloques
            tokenized = tokenizer(doc, return_tensors='pt', truncation=True, max_length=block_size, padding='max_length')
            input_ids = tokenized['input_ids'].squeeze(0)
            self.examples.append(input_ids)

    def __len__(self): return len(self.examples)
    def __getitem__(self, i):
        return {
            "input_ids": self.examples[i],
            "attention_mask": torch.ones_like(self.examples[i]),
            "labels": self.examples[i]
        }

def train_gpt2_range(
    base_dir: str,
    start_date: str,
    end_date: str,
    output_dir: str = './boe_gpt2',
    block_size: int = 512
) -> Tuple[GPT2LMHeadModel, GPT2TokenizerFast]:
    """
    Entrena GPT-2 sobre los archivos XML en el rango de fechas dado.
    """
    files = list_xml_files_in_range(base_dir, start_date, end_date)
    if not files:
        raise ValueError(f"No XML files found in {base_dir} for the given date range: {start_date} to {end_date}")
    tokenizer = GPT2TokenizerFast.from_pretrained('gpt2')
    if tokenizer.eos_token is None:
        tokenizer.add_special_tokens({'eos_token': ''})
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    dataset = BOETextDataset(files, tokenizer, block_size=block_size)
    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
    model = GPT2LMHeadModel.from_pretrained('gpt2')
    model.resize_token_embeddings(len(tokenizer))
    training_args = TrainingArguments(
        output_dir=output_dir,
        overwrite_output_dir=True,
        num_train_epochs=3,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=8,
        learning_rate=5e-5,
        weight_decay=0.01,
        warmup_steps=100,
        logging_steps=50,
        save_steps=500,
        save_total_limit=3,
        fp16=torch.cuda.is_available(),
    )
    trainer = Trainer(model=model, args=training_args, train_dataset=dataset, data_collator=data_collator)
    trainer.train()
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    return model, tokenizer

# ------------------------------------------
# 2) Summarization (BART) + Metaheuristic GA
# ------------------------------------------
class BOESummaryDataset(Dataset):
    """
    Dataset para summarization: extrae texto completo de XML como input y target resumen opcional.
    Aquí se usa sin target para fine-tuning no supervisado o previo.
    """
    def __init__(self, file_list: List[str], tokenizer: BartTokenizerFast, max_length: int = 1024):
        self.tokenizer = tokenizer
        self.files = file_list
        self.max_length = max_length

    def __len__(self): return len(self.files)

    def __getitem__(self, idx):
        path = self.files[idx]
        tree = ET.parse(path)
        root = tree.getroot()
        paragraphs = [p.text for p in root.findall('.//texto//p') if p.text]
        text = " ".join(paragraphs)
        inputs = self.tokenizer(
            text,
            max_length=self.max_length,
            truncation=True,
            padding='max_length',
            return_tensors='pt'
        )
        # labels = inputs.input_ids for unsupervised LM; for supervised, necesitarías resúmenes.
        labels = inputs.input_ids.clone()
        return {k: v.squeeze(0) for k, v in inputs.items()}, labels.squeeze(0)


def train_summarization_range(
    base_dir: str,
    start_date: str,
    end_date: str,
    output_dir: str = './boe_bart',
    max_length: int = 1024
) -> Tuple[BartForConditionalGeneration, BartTokenizerFast]:
    """
    Fine-tuning de BART en modo auto-regresivo sobre textos BOE en rango de fechas.
    """
    files = list_xml_files_in_range(base_dir, start_date, end_date)
    tokenizer = BartTokenizerFast.from_pretrained('facebook/bart-base')
    dataset = BOESummaryDataset(files, tokenizer, max_length=max_length)
    # convertir a formato Trainer
    def collate_fn(batch):
        inputs = {k: torch.stack([x[0][k] for x in batch]) for k in batch[0][0]}
        labels = torch.stack([x[1] for x in batch])
        inputs['labels'] = labels
        return inputs

    training_args = TrainingArguments(
        output_dir=output_dir,
        overwrite_output_dir=True,
        num_train_epochs=3,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        learning_rate=3e-5,
        weight_decay=0.01,
        logging_steps=50,
        save_steps=500,
        save_total_limit=3,
        fp16=torch.cuda.is_available(),
    )
    model = BartForConditionalGeneration.from_pretrained('facebook/bart-base')
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        data_collator=collate_fn
    )
    trainer.train()
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    return model, tokenizer

# ------------------------------------------
# 3) Metaheuristic Extractive Summarizer (GA)
# ------------------------------------------
# (Igual que antes)
class ExtractiveSummarizerGA:
    def __init__(self,
                 population_size: int = 50,
                 generations: int = 30,
                 summary_size: int = 3,
                 crossover_rate: float = 0.8,
                 mutation_rate: float = 0.2):
        self.pop_size = population_size
        self.generations = generations
        self.summary_size = summary_size
        self.cx_rate = crossover_rate
        self.mut_rate = mutation_rate
        self.vectorizer = TfidfVectorizer()

    def _initialize_population(self, n_sentences: int) -> List[np.ndarray]:
        pop = []
        for _ in range(self.pop_size):
            bits = np.zeros(n_sentences, dtype=int)
            ones = np.random.choice(n_sentences, self.summary_size, replace=False)
            bits[ones] = 1
            pop.append(bits)
        return pop

    def _fitness(self, bits: np.ndarray, sent_vectors: np.ndarray, doc_vector: np.ndarray) -> float:
        selected = sent_vectors[bits==1]
        coverage = selected.dot(doc_vector).sum()
        red = 0.0
        for i in range(len(selected)):
            for j in range(i+1, len(selected)):
                red += selected[i].dot(selected[j])
        return coverage - 0.5 * red

    def summarize(self, text: str) -> str:
        import nltk; nltk.download('punkt', quiet=True); nltk.download('punkt_tab', quiet=True)
        from nltk.tokenize import sent_tokenize
        sentences = sent_tokenize(text)
        n = len(sentences)
        if n <= self.summary_size:
            return text
        X = self.vectorizer.fit_transform(sentences).toarray()
        doc_vec = X.mean(axis=0)
        pop = self._initialize_population(n)
        for gen in range(self.generations):
            fitnesses = [self._fitness(ind, X, doc_vec) for ind in pop]
            idx = np.argsort(fitnesses)[-self.pop_size//2:]
            parents = [pop[i] for i in idx]
            offspring = []
            while len(offspring) < self.pop_size:
                if random.random() < self.cx_rate:
                    p1, p2 = random.sample(parents, 2)
                    pt = random.randint(1, n-1)
                    c1 = np.concatenate([p1[:pt], p2[pt:]])
                    c2 = np.concatenate([p2[:pt], p1[pt:]])
                    for c in (c1, c2):
                        diff = c.sum() - self.summary_size
                        if diff > 0:
                            ones = np.where(c==1)[0]
                            drop = np.random.choice(ones, diff, replace=False)
                            c[drop] = 0
                        elif diff < 0:
                            zeros = np.where(c==0)[0]
                            add = np.random.choice(zeros, -diff, replace=False)
                            c[add] = 1
                    offspring.extend([c1, c2])
                else:
                    offspring.append(random.choice(parents).copy())
            for ind in offspring:
                if random.random() < self.mut_rate:
                    ones = np.where(ind==1)[0]
                    zeros = np.where(ind==0)[0]
                    if len(ones)>0 and len(zeros)>0:
                        off = random.choice(ones)
                        on = random.choice(zeros)
                        ind[off], ind[on] = 0, 1
            pop = offspring
        fitnesses = [self._fitness(ind, X, doc_vec) for ind in pop]
        best = pop[int(np.argmax(fitnesses))]
        summary = " ".join([s for bit, s in zip(best, sentences) if bit==1])
        return summary

def generate_boe(model, tokenizer, prompt, max_length=300, num_return_sequences=1, device=None):
    """
    Genera nuevos textos de formato BOE usando el modelo y tokenizer dados.
    Args:
        model: Modelo GPT2LMHeadModel entrenado.
        tokenizer: Tokenizer GPT2TokenizerFast entrenado.
        prompt: Texto de inicio para la generación.
        max_length: Longitud máxima del texto generado.
        num_return_sequences: Número de textos a generar.
        device: 'cuda' o 'cpu'. Si None, se detecta automáticamente.
    Returns:
        Lista de textos generados.
    """
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    model.eval()
    input_ids = tokenizer.encode(prompt, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model.generate(
            input_ids,
            max_length=max_length,
            num_return_sequences=num_return_sequences,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            temperature=0.9,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )
    generated = [tokenizer.decode(out, skip_special_tokens=True) for out in outputs]
    return generated

# ------------------------------------------
# 4) Ejemplo de uso con rango de fechas
# ------------------------------------------
if __name__ == '__main__':
    base_dir = '../../backend/data/boe/diario'
    # rango deseado
    start_date = '01/01/2020'
    end_date   = '01/01/2025'

    # Entrenar generativo
    gpt2_model, gpt2_tokenizer = train_gpt2_range(base_dir, start_date, end_date)

    # Entrenar summarization
    bart_model, bart_tokenizer = train_summarization_range(base_dir, start_date, end_date)

    # Resumen extractivo con GA de un documento ejemplo
    sample_files = list_xml_files_in_range(base_dir, start_date, end_date)
    if sample_files:
        tree = ET.parse(sample_files[0])
        root = tree.getroot()
        text = " ".join([p.text for p in root.findall('.//texto//p') if p.text])
        summarizer = ExtractiveSummarizerGA(population_size=60, generations=40, summary_size=5)
        print("Resumen GA:\n", summarizer.summarize(text))
    
    # Generación condicional
    prompt = "Resolución de la Subsecretaría sobre subvenciones para energías renovables"
    outputs = generate_boe(gpt2_model, gpt2_tokenizer, prompt, max_length=300, num_return_sequences=2)
    for i, out in enumerate(outputs, 1):
        print(f"-- Gen {i} --\n{out}\n")
