from fastapi import APIRouter
from .schemas import SummarizationRequest, SummarizationResponse, SummaryBlock
from .model_loader import load_model
from transformers import AutoTokenizer
from concurrent.futures import ThreadPoolExecutor
import os, json

router = APIRouter()
model_cache = {}
tokenizer_cache = {}

# 模型注册表路径
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
REGISTRY_PATH = os.path.join(BASE_DIR, "model/version_registry.json")
with open(REGISTRY_PATH, "r") as f:
    MODEL_REGISTRY = json.load(f)["models"]

def get_model_and_tokenizer(model_name: str):
    if model_name not in model_cache:
        model_cache[model_name] = load_model(model_name)

    if model_name not in tokenizer_cache:
        model_path = os.path.abspath(os.path.join(BASE_DIR, MODEL_REGISTRY[model_name]["path"]))
        tokenizer_cache[model_name] = AutoTokenizer.from_pretrained(model_path, local_files_only=True)

    return model_cache[model_name], tokenizer_cache[model_name]

def recursive_summarize_blocks(summarizer, tokenizer, texts, max_token_len=512, max_depth=5, do_sample=False):
    current_depth = 1
    hierarchy = [[{"text": t} for t in texts]]
    current_blocks = texts.copy()

    if not current_blocks:
        return "", hierarchy, 0

    while current_depth <= max_depth:
        groups = []
        group = []
        token_len = 0

        # ✅ 智能合并多个 blocks，逼近 token 上限
        for i, t in enumerate(current_blocks):
            l = len(tokenizer(t)["input_ids"])
            if token_len + l > max_token_len:
                if group:
                    groups.append(group)
                group = [(i, t)]
                token_len = l
            else:
                group.append((i, t))
                token_len += l
        if group:
            groups.append(group)

        # ✅ 若只剩 1 个 group，仍然走一轮 summary（确保 summary 被调用）
        compressed = []
        for g in groups:
            indices, texts_in_group = zip(*g)
            merged = "\n".join(texts_in_group)
            try:
                out = summarizer(merged, max_length=512, min_length=100, do_sample=do_sample)
                compressed.append({
                    "text": out[0]["summary_text"],
                    "sources": list(indices)
                })
            except Exception as e:
                print(f"[ERROR] summarizing group failed: {e}")
                continue

        if not compressed:
            break

        hierarchy.append(compressed)
        current_blocks = [b["text"] for b in compressed]
        current_depth += 1

        # ✅ 若已压缩到只剩 1 条且 token 不超长，可终止递归
        merged = "\n".join(current_blocks)
        if len(current_blocks) == 1 and len(tokenizer(merged)["input_ids"]) <= max_token_len:
            break

    final_summary = current_blocks[0] if current_blocks else ""
    return final_summary, hierarchy, current_depth

@router.post("/summarize_recursive", response_model=SummarizationResponse)
def summarize_recursive(req: SummarizationRequest):
    model_name = req.model_name or "t5_small"
    summarizer, tokenizer = get_model_and_tokenizer(model_name)

    paragraphs = [p.strip() for p in req.text.split("\n\n") if p.strip()]
    if not paragraphs:
        return SummarizationResponse(summary="", details=[], depth=0, hierarchy=[])

    # 并行处理第一层段落
    def summarize_one(para):
        tokens = tokenizer(para)["input_ids"]
        chunk_size = 400
        chunks = []

        for i in range(0, len(tokens), chunk_size):
            chunk = tokens[i:i+chunk_size]
            text_chunk = tokenizer.decode(chunk, skip_special_tokens=True)
            chunks.append(text_chunk.strip())

        # 对多个 chunk 分别摘要，再合并成一级摘要结果
        summaries = []
        for chunk in chunks:
            try:
                out = summarizer(chunk, max_length=256, min_length=30, do_sample=req.do_sample)
                summaries.append(out[0]["summary_text"])
            except Exception as e:
                print(f"[ERROR] summarize_one chunk failed: {e}")
                continue

        return "\n".join(summaries)


    with ThreadPoolExecutor(max_workers=min(len(paragraphs), os.cpu_count() or 4)) as executor:
        level1_summaries = list(executor.map(summarize_one, paragraphs))

    final_summary, hierarchy, depth = recursive_summarize_blocks(
        summarizer, tokenizer, level1_summaries, do_sample=req.do_sample
    )

    return SummarizationResponse(
        summary=final_summary,
        details=level1_summaries,
        depth=depth,
        hierarchy=hierarchy
    )
