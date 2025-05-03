import os
import json
import argparse
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

def update_registry(model_name: str, save_dir: str):
    registry_path = os.path.join("model", "version_registry.json")
    key_name = os.path.basename(os.path.normpath(save_dir))  # 提取最后一段作为 key

    if os.path.exists(registry_path):
        with open(registry_path, "r") as f:
            registry = json.load(f)
    else:
        registry = {"models": {}}

    registry["models"][key_name] = {
        "description": f"Local model: {model_name}",
        "path": save_dir
    }

    with open(registry_path, "w") as f:
        json.dump(registry, f, indent=2)
    
    print(f"📘 Updated version_registry.json with key: {key_name}")

def download_and_save(model_name: str, save_dir: str):
    print(f"📥 Downloading model from HuggingFace: {model_name}")
    
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    os.makedirs(save_dir, exist_ok=True)
    model.save_pretrained(save_dir)
    tokenizer.save_pretrained(save_dir)

    print(f"✅ Model saved to: {save_dir}")
    update_registry(model_name, save_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="Model name from HuggingFace (e.g., t5-small)")
    parser.add_argument("--out", required=True, help="Local directory to save the model (e.g., model/t5_small)")

    args = parser.parse_args()
    download_and_save(args.model, args.out)
