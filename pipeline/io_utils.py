import base64
import io
import json
import os
from typing import Any

from PIL import Image

def read_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_json(path: str, obj: Any) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def load_rgba(path: str) -> Image.Image:
    return Image.open(path).convert("RGBA")

def merge_source_and_layer(source_path: str, layer_path: str) -> Image.Image:
    src = load_rgba(source_path)
    if layer_path and os.path.exists(layer_path):
        layer = load_rgba(layer_path)
        if layer.size != src.size:
            layer = layer.resize(src.size, resample=Image.BICUBIC)
        out = src.copy()
        out.alpha_composite(layer)
        return out
    return src

def pil_to_data_url(img: Image.Image, fmt: str = "PNG") -> str:
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/{fmt.lower()};base64,{b64}"
