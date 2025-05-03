import os
import xml.etree.ElementTree as ET
from typing import List, Tuple

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
# 1) Generative Model (GPT-2)
# -------------------------------
class BOETextDataset(Dataset):
    def __init__(
        self,
        xml_dir: str,
        tokenizer: GPT2TokenizerFast,
        block_size: int = 512,
    ):
        self.tokenizer = tokenizer
        self.block_size = block_size
        self.examples = []
        raw_texts = []
        for fn in os.listdir(xml_dir):
            if not fn.endswith('.xml'): continue
            path = os.path.join(xml_dir, fn)
            tree = ET.parse(path)
            root = tree.getroot()
            title = root.findtext('.//titulo') or ''
            paragraphs = [p.text for p in root.findall('.//texto//p') if p.text]
            body = "\n".join(paragraphs)
            doc = f"<TITULO> {title} </TITULO>\n<BODY> {body} </BODY>"
            raw_texts.append(doc)
        concatenated = "\n".join(raw_texts)
        tokenized = tokenizer(concatenated, return_tensors='pt')
        input_ids = tokenized['input_ids'].squeeze(0)
        for i in range(0, input_ids.size(0) - block_size + 1, block_size):
            block = input_ids[i:i + block_size]
            self.examples.append(block)

    def __len__(self): return len(self.examples)
    def __getitem__(self, i):
        return {"input_ids": self.examples[i], "attention_mask": torch.ones_like(self.examples[i]), "labels": self.examples[i]}


def train_gpt2(xml_dir: str, output_dir: str = './boe_gpt2'):
    tokenizer = GPT2TokenizerFast.from_pretrained('gpt2')
    if tokenizer.eos_token is None:
        tokenizer.add_special_tokens({'eos_token': ''})
    dataset = BOETextDataset(xml_dir, tokenizer, block_size=512)
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


def generate_boe(model: GPT2LMHeadModel, tokenizer: GPT2TokenizerFast, prompt: str, max_length: int = 512, num_return_sequences: int = 1) -> List[str]:
    inputs = tokenizer(prompt, return_tensors='pt')
    output_sequences = model.generate(
        input_ids=inputs['input_ids'].to(model.device),
        attention_mask=inputs['attention_mask'].to(model.device),
        max_length=max_length,
        do_sample=True,
        top_k=50,
        top_p=0.95,
        temperature=1.0,
        num_return_sequences=num_return_sequences,
        eos_token_id=tokenizer.eos_token_id
    )
    return [tokenizer.decode(seq, skip_special_tokens=True) for seq in output_sequences]

# ------------------------------------------
# 2) Extractive Summarization with Metaheuristic
# ------------------------------------------
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
            # bit vector with exactly summary_size ones
            bits = np.zeros(n_sentences, dtype=int)
            ones = np.random.choice(n_sentences, self.summary_size, replace=False)
            bits[ones] = 1
            pop.append(bits)
        return pop

    def _fitness(self, bits: np.ndarray, sent_vectors: np.ndarray, doc_vector: np.ndarray) -> float:
        # coverage: sum similarity selected sentences to doc
        selected = sent_vectors[bits==1]
        coverage = selected.dot(doc_vector).sum()
        # redundancy: sum pairwise similarities among selected
        red = 0.0
        for i in range(len(selected)):
            for j in range(i+1, len(selected)):
                red += selected[i].dot(selected[j])
        # maximize coverage, minimize redundancy
        return coverage - 0.5 * red

    def summarize(self, text: str) -> str:
        # split into sentences
        import nltk; nltk.download('punkt', quiet=True)
        from nltk.tokenize import sent_tokenize
        sentences = sent_tokenize(text)
        n = len(sentences)
        if n <= self.summary_size:
            return text
        # tf-idf vectors
        X = self.vectorizer.fit_transform(sentences).toarray()
        # document vector
        doc_vec = X.mean(axis=0)
        # population
        pop = self._initialize_population(n)
        # evolution
        for gen in range(self.generations):
            # evaluate fitness
            fitnesses = [self._fitness(ind, X, doc_vec) for ind in pop]
            # select top half
            idx = np.argsort(fitnesses)[-self.pop_size//2:]
            parents = [pop[i] for i in idx]
            # create offspring
            offspring = []
            while len(offspring) < self.pop_size:
                if random.random() < self.cx_rate:
                    p1, p2 = random.sample(parents, 2)
                    # one-point crossover
                    pt = random.randint(1, n-1)
                    c1 = np.concatenate([p1[:pt], p2[pt:]])
                    c2 = np.concatenate([p2[:pt], p1[pt:]])
                    # repair to summary_size ones
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
            # mutation
            for ind in offspring:
                if random.random() < self.mut_rate:
                    # flip one bit on and one off to maintain size
                    ones = np.where(ind==1)[0]
                    zeros = np.where(ind==0)[0]
                    if len(ones)>0 and len(zeros)>0:
                        off = random.choice(ones)
                        on = random.choice(zeros)
                        ind[off], ind[on] = 0, 1
            pop = offspring
        # best individual
        fitnesses = [self._fitness(ind, X, doc_vec) for ind in pop]
        best = pop[int(np.argmax(fitnesses))]
        summary = " ".join([s for bit, s in zip(best, sentences) if bit==1])
        return summary

# ------------------------------------------
# 3) Example usage
# ------------------------------------------
if __name__ == '__main__':
    xml_dir = '../../backend/data/boe/'  # Directory with XML files

    # 3.1 Entrenar GPT-2 generativo
    gpt2_model, gpt2_tokenizer = train_gpt2(xml_dir)
    prompt = "Resolución de la Subsecretaría sobre subvenciones para energías renovables"
    gens = generate_boe(gpt2_model, gpt2_tokenizer, prompt, max_length=300, num_return_sequences=2)
    for i, doc in enumerate(gens, 1):
        print(f"--- Documento generado {i} ---\n{doc}\n")

    # 3.2 Resumir un documento con GA
    # Cargar un XML de ejemplo
    sample_xml = os.path.join(xml_dir, os.listdir(xml_dir)[0])
    tree = ET.parse(sample_xml)
    root = tree.getroot()
    paragraphs = [p.text for p in root.findall('.//texto//p') if p.text]
    text = " ".join(paragraphs)
    summarizer = ExtractiveSummarizerGA(population_size=60, generations=40, summary_size=5)
    summary = summarizer.summarize(text)
    print("--- Resumen extractivo (GA) ---\n", summary)
