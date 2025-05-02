import os
import argparse
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

def download_and_save(model_name: str, save_dir: str):
    print(f"📥 Downloading model: {model_name}")
    
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    os.makedirs(save_dir, exist_ok=True)
    model.save_pretrained(save_dir)
    tokenizer.save_pretrained(save_dir)

    print(f"✅ Model and tokenizer saved to: {save_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and save HuggingFace Seq2Seq model locally.")
    parser.add_argument(
        "--model", type=str, default="facebook/bart-large-cnn",
        help="Model name from HuggingFace Hub (e.g., 'facebook/bart-large-cnn', 't5-small')"
    )
    parser.add_argument(
        "--out", type=str, default="./model/base_model",
        help="Output directory to save model and tokenizer"
    )

    args = parser.parse_args()
    download_and_save(args.model, args.out)
