# BOE Text Generator and Summarizer

- **Listado de ficheros XML por rango de fechas**

  ```python
  def list_xml_files_in_range(base_dir, start_date, end_date):
      """
      Recorre la estructura `base_dir/YYYY/YYYYMMDD/xml/*.xml`,
      convierte carpetas `YYYYMMDD` a fechas, filtra por rango,
      y devuelve rutas de archivos `.xml`.
      """
      # … implementación …
  ```

- **Generación de documentos BOE (GPT-2)**  
  1. **Dataset** (`BOETextDataset`):
     - Extrae `<titulo>` y `<p>` de `<texto>`, concatena, tokeniza y crea bloques de tamaño fijo.  
  2. **Entrenamiento** (`train_gpt2_range`):

     ```python
     def train_gpt2_range(base_dir, start_date, end_date, output_dir, block_size):
         files = list_xml_files_in_range(base_dir, start_date, end_date)
         dataset = BOETextDataset(files, tokenizer, block_size)
         trainer = Trainer(
             model=GPT2LMHeadModel.from_pretrained('gpt2'),
             args=TrainingArguments(output_dir=output_dir, …),
             train_dataset=dataset,
             data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False)
         )
         trainer.train()
         trainer.save_model(output_dir)
         return model, tokenizer
     ```

  3. **Generación** (`generate_boe`):

     ```python
     def generate_boe(model, tokenizer, prompt, max_length, num_return_sequences):
         inputs = tokenizer(prompt, return_tensors='pt')
         outputs = model.generate(
             input_ids=inputs.input_ids,
             attention_mask=inputs.attention_mask,
             max_length=max_length,
             do_sample=True, top_k=50, top_p=0.95
         )
         return [tokenizer.decode(o) for o in outputs]
     ```

- **Fine‑tuning de BART para summarization**  
  1. **Dataset** (`BOESummaryDataset`):
     - Tokeniza el texto completo de cada XML para encoder‑decoder.  
  2. **Entrenamiento** (`train_summarization_range`):

     ```python
     def train_summarization_range(base_dir, start_date, end_date, output_dir):
         files = list_xml_files_in_range(base_dir, start_date, end_date)
         dataset = BOESummaryDataset(files, tokenizer, max_length)
         trainer = Trainer(
             model=BartForConditionalGeneration.from_pretrained('facebook/bart-base'),
             args=TrainingArguments(output_dir=output_dir, …),
             train_dataset=dataset,
             data_collator=collate_fn
         )
         trainer.train()
         trainer.save_model(output_dir)
         return model, tokenizer
     ```

- **Resumidor extractivo con Algoritmo Genético**

  ```python
  class ExtractiveSummarizerGA:
      def __init__(self, population_size, generations, summary_size, …):
          # Parámetros GA y TF‑IDF vectorizer
      def summarize(self, text) -> str:
          # 1. Tokeniza en oraciones
          # 2. Representa oraciones/doc con TF‑IDF
          # 3. Inicializa población de vectores binarios
          # 4. Itera: fitness = cobertura – λ·redundancia, selección, cruce, mutación
          # 5. Devuelve las N oraciones mejor valoradas
  ```

- **Flujo principal** (`__main__`):  
  1. Definir `base_dir = 'backend/data/boe/diario'` y rango `06/01/2023–21/03/2024`.  
  2. Ejecutar `train_gpt2_range(...)` y `train_summarization_range(...)`.  
  3. Resumir un documento ejemplo con `ExtractiveSummarizerGA.summarize(...)`.  
  4. Generar nuevos BOE con `generate_boe(...)`.
