import requests
from config import HF_API_KEY

# Plagiarism-Light Checker (Paraphrase Similarity)
# Idea: If two answers mean the same thing, similarity will be high.
MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
API_URL = f"https://router.huggingface.co/hf-inference/models/{MODEL_ID}"
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

PAIRS = [
    ("Plants make food using sunlight, water, and carbon dioxide.",
     "Plants create their own food with light, water and CO2."),
    ("The water cycle includes evaporation, condensation, and precipitation.",
     "Water evaporates, forms clouds, and then falls as rain."),
    ("A fraction shows a part of a whole, like 1/2 of a pizza.",
     "Fractions represent pieces of something, like half a pizza."),
    ("Python lists can store many values in one variable.",
     "A list in Python keeps multiple items together in one place."),
    ("Rome is the capital of Italy and it has many ancient buildings.",
     "Italy's capital is Rome, famous for old historical monuments."),
    ("I love summer because I can play outside for longer.",
     "Summer is my favorite since I get extra time to play outdoors.")
]

def similarity(a: str, b: str) -> float:
    payload = {"inputs": {"source_sentence": a, "sentences": [b]}}
    r = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
    if not r.ok: raise RuntimeError(f"HF error {r.status_code}: {r.text}")
    data = r.json()
    if isinstance(data, dict): raise RuntimeError(data.get("error", str(data)))
    return float(data[0])  # 0 to 1

def bar(score01: float) -> str:
    blocks = int((score01 * 100) // 10)
    return "█" * blocks + "░" * (10 - blocks)

def verdict(score01: float, threshold: float) -> str:
    if score01 >= threshold:
        return "⚠️ TOO SIMILAR (possible copy)"
    if score01 >= threshold - 0.15:
        return "🤔 KIND OF SIMILAR"
    return "✅ DIFFERENT ENOUGH"

def main():
    print("📝 Plagiarism-Light Checker (Paraphrase Similarity)")
    print("This checks if two answers are TOO similar in meaning.\n")
    threshold = 0.80
    print(f"Rule: If similarity ≥ {threshold}, we say 'Too Similar'.\n")

    while True:
        print("Type 'demo' to test examples, or 'custom' to type your own, or 'exit'.")
        mode = input("Mode: ").strip().lower()
        if mode == "exit":
            print("Bye! 🚀")
            break

        if mode == "demo":
            for i, (a1, a2) in enumerate(PAIRS[:5], 1):
                s = similarity(a1, a2)
                pct = round(s * 100, 1)
                print(f"\n{i}) Answer 1: {a1}\n   Answer 2: {a2}")
                print(f"   Similarity: {pct}% [{bar(s)}]  {verdict(s, threshold)}")

        elif mode == "custom":
            a1 = input("\nStudent Answer 1: ").strip()
            a2 = input("Student Answer 2: ").strip()
            if not a1 or not a2:
                print("Please type both answers.\n")
                continue
            s = similarity(a1, a2)
            pct = round(s * 100, 1)
            print(f"\nSimilarity: {pct}% [{bar(s)}]  {verdict(s, threshold)}\n")

        else:
            print("Please type: demo / custom / exit\n")

if __name__ == "__main__":
    main()
