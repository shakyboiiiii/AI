import os
from io import BytesIO
from PIL import Image
import numpy as np
import cv2
from huggingface_hub import InferenceClient
from config import HF_API_KEY
PROVIDERS = ["hf-inference", "wavespeed", "fal-ai"]
MODELS = ["Qwen/Qwen-Image-Edit", "Qwen/Qwen-Image-Edit-2509"]
def must_exist(p, label):
    if not os.path.exists(p):
        raise FileNotFoundError(f"{label} file not found: {p}")
def make_hole_png(image_path, mask_path) -> bytes:
    img = Image.open(image_path).convert("RGBA")
    m = Image.open(mask_path).convert("L")
    if m.size != img.size:
        m = m.resize(img.size, Image.NEAREST)
    alpha = Image.eval(m, lambda p: 255 - p)
    r, g, b, _ = img.split()
    out = Image.merge("RGBA", (r, g, b, alpha))
    buf = BytesIO()
    out.save(buf, format="PNG")
    return buf.getvalue()
def try_hf_edit(prompt: str, hole_png: bytes):
    last = None
    for provider in PROVIDERS:
        client = InferenceClient(provider=provider, api_key=HF_API_KEY)
        for model in MODELS:
            try:
                res = client.image_to_image(
                    hole_png,
                    model=model,
                    prompt=(f"{prompt}. Fill ONLY the transparent parts realistically; keep the rest unchanged. "
                            "Restore scratches/noise/fading subtly. No cartoon style.")
                )
                if isinstance(res, Image.Image):
                    return res, None
                if isinstance(res, (bytes, bytearray)):
                    return Image.open(BytesIO(res)), None
                last = f"{provider}/{model}: unexpected output {type(res)}"
            except Exception as e:
                msg = str(e)
                if "402" in msg or "Payment Required" in msg or "pre-paid credits" in msg.lower():
                    last = f"{provider}/{model}: 402 paid credits required"
                    break
                if "404" in msg or "Not Found" in msg:
                    last = f"{provider}/{model}: 404 not available"
                    continue
                last = f"{provider}/{model}: {e}"
    return None, last or "HF edit not available"
def local_inpaint(image_path: str, mask_path: str) -> Image.Image:
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        raise Exception("Failed to read image for local inpaint.")
    m = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    if m is None:
        raise Exception("Failed to read mask for local inpaint.")
    h, w = img.shape[:2]
    if (m.shape[0], m.shape[1]) != (h, w):
        m = cv2.resize(m, (w, h), interpolation=cv2.INTER_NEAREST)
    _, m_bin = cv2.threshold(m, 127, 255, cv2.THRESH_BINARY)
    out = cv2.inpaint(img, m_bin, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
    out_rgb = cv2.cvtColor(out, cv2.COLOR_BGR2RGB)
    return Image.fromarray(out_rgb)
def main():
    print("=== Vintage Photo Healer ===")
    prompt = input("Describe the restoration (or type 'exit'): ").strip()
    if prompt.lower() == "exit":
        return
    image_path = input("Enter old photo path (default: old_photo.png): ").strip() or "old_photo.png"
    mask_path = input("Enter mask path (default: old_photo_mask.png): ").strip() or "old_photo_mask.png"
    try:
        must_exist(image_path, "Image")
        must_exist(mask_path, "Mask")
        hole_png = make_hole_png(image_path, mask_path)
        fixed, err = try_hf_edit(prompt, hole_png)
        if fixed is None:
            print(f"HF restore unavailable ({err}). Using local inpainting instead.")
            fixed = local_inpaint(image_path, mask_path)
        fixed.show()
        if input("Save restored image? (yes/no): ").strip().lower() == "yes":
            out_path = input("Output filename (default: old_photo_restored.png): ").strip() or "old_photo_restored.png"
            fixed.save(out_path)
            print(f"Saved as {out_path}")
    except Exception as e:
        print(f"Error: {e}")
if __name__ == "__main__":
    main()
