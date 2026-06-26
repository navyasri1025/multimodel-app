from dotenv import load_dotenv
import os
import time
from pathlib import Path
from openai import OpenAI, APITimeoutError
from tabulate import tabulate

load_dotenv(Path(__file__).parent / ".env")

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise RuntimeError("OPENROUTER_API_KEY not found in .env")

client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
    timeout=20,
)

MODELS = [
    "openai/gpt-4o-mini",
    "meta-llama/llama-3.3-70b-instruct",
    "mistralai/mistral-large-2512",
    "qwen/qwen-2.5-72b-instruct",
]

PRICES = {
    "openai/gpt-4o-mini":                {"input": 0.15, "output": 0.60},
    "meta-llama/llama-3.3-70b-instruct": {"input": 0.59, "output": 0.79},
    "mistralai/mistral-large-2512":      {"input": 0.50, "output": 1.50},
    "qwen/qwen-2.5-72b-instruct":        {"input": 0.36, "output": 0.40},
}


def ask(question, model):
    try:
        start = time.time()
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": question}],
            max_tokens=500,
        )
        latency = time.time() - start
        p = PRICES.get(model, {"input": 0.0, "output": 0.0})
        total_tokens = response.usage.prompt_tokens + response.usage.completion_tokens
        cost = (response.usage.prompt_tokens * p["input"] +
                response.usage.completion_tokens * p["output"]) / 1_000_000
        return response.choices[0].message.content, latency, cost, total_tokens
    except APITimeoutError:
        return "Request timed out (>20s)", None, None, None
    except Exception as e:
        return f"{type(e).__name__}: {e}", None, None, None


if __name__ == "__main__":
    QUESTION = input("Enter your question: ")

    rows = []
    for model in MODELS:
        answer, latency, cost, total_tokens = ask(QUESTION, model)
        preview  = answer[:60] + "..." if len(answer) > 60 else answer
        lat_str  = f"{latency:.2f}s"  if latency      is not None else "ERROR"
        cost_str = f"${cost:.6f}"     if cost         is not None else "-"
        tok_str  = str(total_tokens)  if total_tokens is not None else "-"
        rows.append([model, preview, lat_str, cost_str, tok_str])

    print()
    print(tabulate(
        rows,
        headers=["Model Name", "Answer Preview", "Latency (s)", "Cost (USD)", "Tokens"],
        tablefmt="grid",
    ))
