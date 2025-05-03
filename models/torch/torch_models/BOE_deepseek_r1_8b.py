import os
import json
import torch
from datasets import load_dataset
from transformers import (
    AutoConfig,
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from huggingface_hub import snapshot_download

# Paths
OLLAMA_DIR = "/mnt/hdd1:2TB/models/ollama"
MODEL_NAME = "deepseek-r1"
TAG = "8b"
MANIFEST_PATH = os.path.join(
    OLLAMA_DIR,
    f"manifests/registry.ollama.ai/library/{MODEL_NAME}/{TAG}"
)

# 1) Read manifest to get GGUF digest
with open(MANIFEST_PATH, "r") as f:
    manifest = json.load(f)
digest = next(
    layer["digest"] for layer in manifest["layers"]
    if layer["mediaType"] == "application/vnd.ollama.image.model"
)

# 2) Build path to the GGUF blob
GGUF_FILE = os.path.join(OLLAMA_DIR, "blobs/sha256", digest)
print(f"Using GGUF file: {GGUF_FILE}")

# 3) Snapshot HF repo locally (to get custom model code)
HF_REPO = "deepseek-ai/DeepSeek-R1"
hf_local = snapshot_download(HF_REPO, repo_type="model", local_dir="/mnt/hdd1:2TB/models/hf")  # downloads config, tokenizer, modeling code locally
print(f"Hugging Face repo snapshot at: {hf_local}")

# 4) Load config, tokenizer & model from local HF snapshot
tokenizer = AutoTokenizer.from_pretrained(
    hf_local,
    trust_remote_code=True,
    use_fast=True,
    local_files_only=True
)
config = AutoConfig.from_pretrained(
    hf_local,
    trust_remote_code=True,
    local_files_only=True
)
model = AutoModelForCausalLM.from_pretrained(
    hf_local,
    gguf_file=GGUF_FILE,
    config=config,
    trust_remote_code=True,
    torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
    local_files_only=True
)

# 5) Load dataset
DATA_PATH = "./boe_dataset.jsonl"
dataset = load_dataset("json", data_files=DATA_PATH, split="train")

# 6) Preprocess: join input/output as prompt and set labels
def preprocess(example):
    prompt = example["input"].strip() + "\n" + example["output"].strip()
    tok = tokenizer(
        prompt,
        truncation=True,
        max_length=2048,
        padding="max_length"
    )
    tok["labels"] = tok["input_ids"].copy()
    return tok

tokenized_dataset = dataset.map(preprocess, batched=False)

# 7) Data collator & training arguments
data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
OUTPUT_DIR = "/mnt/hdd1:2TB/models/finetuned/BOE_deepseek_r1_8b"
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

# 8) Trainer & train
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    data_collator=data_collator,
    tokenizer=tokenizer
)

trainer.train()
trainer.save_model()
tokenizer.save_pretrained(OUTPUT_DIR)
print(f"Fine-tuned model saved to {OUTPUT_DIR}")
