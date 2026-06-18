from __future__ import annotations
import os
from openai import OpenAI
from .schemas import QAExample, JudgeResult, ReflectionEntry
from .prompts import ACTOR_SYSTEM, EVALUATOR_SYSTEM, REFLECTOR_SYSTEM
from .utils import normalize_answer

# Cấu hình kết nối tới Local Model (Ollama, vLLM, LM Studio,...)
# Mặc định Ollama cung cấp API tương thích OpenAI tại port 11434
LOCAL_BASE_URL = os.getenv("LOCAL_BASE_URL", "http://localhost:11434/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5:1.5b") # Đã tự động đổi thành model máy đang có

client = OpenAI(
    base_url=LOCAL_BASE_URL,
    api_key="local-no-key-needed" # API key cục bộ không quan trọng
)

def format_context(context_list) -> str:
    return "\n\n".join([f"--- Document: {c.title} ---\n{c.text}" for c in context_list])

def actor_answer(example: QAExample, attempt_id: int, agent_type: str, reflection_memory: list[str]) -> tuple[str, int]:
    context_str = format_context(example.context)
    user_prompt = f"Question: {example.question}\n\nContext:\n{context_str}\n"
    
    if reflection_memory:
        memories = "\n".join(reflection_memory)
        user_prompt += f"\nReflection Memory (DO NOT REPEAT THESE MISTAKES):\n{memories}\n"

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": ACTOR_SYSTEM},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.0
    )
    tokens = response.usage.total_tokens if response.usage else 0
    return response.choices[0].message.content.strip(), tokens

def evaluator(example: QAExample, answer: str) -> tuple[JudgeResult, int]:
    # Tối ưu: Nếu đáp án khớp 100% thì không cần gọi LLM chấm điểm cho tốn thời gian
    if normalize_answer(example.gold_answer) == normalize_answer(answer):
        return JudgeResult(score=1, reason="Final answer matches the gold answer perfectly.", missing_evidence=[], spurious_claims=[]), 0

    user_prompt = f"Question: {example.question}\nGold Answer: {example.gold_answer}\nPredicted Answer: {answer}"
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": EVALUATOR_SYSTEM},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.0,
        response_format={"type": "json_object"}
    )
    
    tokens = response.usage.total_tokens if response.usage else 0
    try:
        content = response.choices[0].message.content
        return JudgeResult.model_validate_json(content), tokens
    except Exception as e:
        return JudgeResult(score=0, reason=f"Model failed to return JSON: {str(e)}", missing_evidence=[], spurious_claims=[]), tokens

def reflector(example: QAExample, attempt_id: int, judge: JudgeResult, answer: str) -> tuple[ReflectionEntry, int]:
    user_prompt = f"Attempt ID: {attempt_id}\nQuestion: {example.question}\nWrong Answer: {answer}\nEvaluator Reason: {judge.reason}"
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": REFLECTOR_SYSTEM},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.0,
        response_format={"type": "json_object"}
    )
    
    tokens = response.usage.total_tokens if response.usage else 0
    try:
        content = response.choices[0].message.content
        return ReflectionEntry.model_validate_json(content), tokens
    except Exception as e:
        return ReflectionEntry(
            attempt_id=attempt_id,
            failure_reason=judge.reason,
            lesson=f"JSON parsing error: {str(e)}",
            next_strategy="Pay closer attention to the question requirements and ensure proper formatting."
        ), tokens
