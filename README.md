# 📄 Summarizer System

A fully containerized, modular text summarization system designed for **private deployment**, **user interaction**, and **lightweight fine-tuning**. The system is structured into three core services:

- 🌐 A frontend interface built with Vue + TailwindCSS
- ⚙️ A backend API powered by FastAPI
- 🧠 A local model engine based on BART with LoRA fine-tuning support

---

## 📦 System Architecture

> Unified via Docker for seamless local deployment

```plaintext
📦 Docker Deployment
├── 🌐 Frontend (Vue + Tailwind)
│   ├── Text Input (Single / Batch / PDF)
│   ├── Model Selector (BART / LoRA)
│   ├── Configuration (length / style)
│   ├── Upload Training Data
│   ├── Trigger Fine-Tuning + Logs
│   └── Result View + Export (TXT / PDF)
├── ⚙️ Backend API (FastAPI)
│   ├── POST /summarize
│   ├── POST /train_lora
│   └── GET /models, /status
└── 🧠 Model Engine
    ├── Load Local BART
    ├── Load LoRA Weights
    ├── Inference Pipeline Wrapper
    ├── Fine-tuning Logs
    └── Model Version Registry

1. python download_model.py --model t5-small --out model/t5_small
(python download_model.py --model sshleifer/distilbart-cnn-12-6 --out model/distilbart_cnn)
2. docker compose up