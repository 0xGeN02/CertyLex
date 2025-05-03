import torch
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer, DataCollatorForLanguageModeling

MODEL_PATH = "/mnt/hdd1:2TB/models/ollama"  # Cambia esto a tu ruta local
DATA_PATH = "../boe_dataset.jsonl"
OUTPUT_DIR = "/mnt/hdd1:2TB/models/finetuned/BOE_deepseek_r1_8b"

# 1. Cargar dataset
dataset = load_dataset("json", data_files=DATA_PATH, split="train")

# 2. Tokenizer y modelo
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, trust_remote_code=True, torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32)

# 3. Preprocesamiento: concatenar input y output como prompt
def preprocess(example):
    prompt = example["input"].strip() + "\n" + example["output"].strip()
    tokens = tokenizer(prompt, truncation=True, max_length=2048, padding="max_length")
    tokens["labels"] = tokens["input_ids"].copy()
    return tokens

tokenized_dataset = dataset.map(preprocess, batched=False)

# 4. Data collator
data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

# 5. Training arguments
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=8,
    num_train_epochs=1,
    learning_rate=2e-5,
    fp16=torch.cuda.is_available(),
    save_steps=500,
    logging_steps=50,
    save_total_limit=2,
    report_to="none"
)

# 6. Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    data_collator=data_collator,
    tokenizer=tokenizer
)

# 7. Entrenamiento
trainer.train()
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
