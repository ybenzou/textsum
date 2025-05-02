import os
import json
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from peft import PeftModel

model_cache = {}

def load_model(model_name: str):
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    REGISTRY_PATH = os.path.join(BASE_DIR, "model/version_registry.json")

    with open(REGISTRY_PATH, "r") as f:
        registry = json.load(f)

    if model_name not in registry["models"]:
        raise ValueError(f"Model {model_name} not found in registry.")

    model_info = registry["models"][model_name]
    model_path = os.path.abspath(os.path.join(BASE_DIR, model_info["path"]))

    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_path, local_files_only=True)

    if "lora" in model_name.lower():
        model = PeftModel.from_pretrained(model, model_path, local_files_only=True)

    # ✅ 自动检测是否有 GPU
    device = 0 if torch.cuda.is_available() else -1

    pipe = pipeline(
        "summarization",
        model=model,
        tokenizer=tokenizer,
        device=device,
        truncation=True,
        model_kwargs={"max_length": 512}
    )
    return pipe
