import os
import time
import openai
from typing import Any, Dict, Optional, Tuple

from PIL import Image

from .client import make_client, get_deployment_name
from .config import TASK_CONFIG
from .io_utils import read_json, merge_source_and_layer, pil_to_data_url, read_text, load_rgba

# Tasks where we want to remove the residual-mark clause from Visual_Coherence prompt
VC_PROMPT_CLAUSE_REMOVE_TASKS = [
    "Addition",
]

VC_RESIDUAL_CLAUSE = "- residual visual instruction marks such as arrows, boxes, strokes, or masks that should not appear in the final image."

USE_LAST_TWO_IMAGES_METRICS = [
    "Contextual_Preservation",
    "Pose_Consistency",
    "Light_Direction_Consistency",
    "Wind_Direction_Consistency",
    "Wind_Contextual_Preservation",
    "Orientation_Alignment",
    "Reorientation_Contextual_Preservation",
    "Billiards"
]

USE_FIRST_AND_LAST_IMAGES_METRICS = [
    "BII_CIC_CP",
]

def maybe_modify_visual_coherence_prompt(task_name: str, metric_name: str, prompt: str) -> str:
    if metric_name == "Visual_Coherence" and task_name in VC_PROMPT_CLAUSE_REMOVE_TASKS:
        return prompt.replace(VC_RESIDUAL_CLAUSE, "")
    return prompt

def find_annotation_item(task_name: str, sample_id: str) -> Optional[Dict[str, Any]]:
    cfg = TASK_CONFIG.get(task_name)
    if not cfg:
        return None
    data = read_json(cfg["json_path"])
    for it in data:
        if str(it.get("id")) == str(sample_id):
            return it
    return None


def resolve_source_and_layer_paths(task_name: str, ann_item: Dict[str, Any]) -> Tuple[str, str]:
    cfg = TASK_CONFIG[task_name]
    image_root = cfg["image_root"]
    task_dir = cfg["task_dir"]

    source_rel = ann_item["file_paths"]["source"]
    layer_rel = ann_item["file_paths"].get("visual_instruction", "")

    source_abs = os.path.join(image_root, source_rel)
    layer_abs = os.path.join(task_dir, layer_rel) if layer_rel else ""
    return source_abs, layer_abs

def resolve_input_and_target_paths(task_name: str, ann_item: Dict[str, Any]) -> Tuple[str, str]:
    cfg = TASK_CONFIG[task_name]
    image_root = cfg["image_root"]
    task_dir = cfg["task_dir"]

    input_rel = ann_item["file_paths"]["source"]
    target_rel = ann_item["file_paths"]["target"]

    input_abs = os.path.join(image_root, input_rel)
    target_abs = os.path.join(task_dir, target_rel) 
    return input_abs, target_abs


def evaluate_one(
    task_name: str,
    sample_id: str,
    prompt_txt_path: str,
    gen_image_abs: str,
    per_item_input_prompt: Optional[str] = None,
    metric_name: Optional[str] = None,
    metric_spec: Optional[Any] = None,   # MetricSpec，提供 parse_fn
) -> Dict[str, Any]:
    """
    Calls GPT once per metric per sample, with retries.
    Will keep retrying API calls until `metric_spec.parse_fn(text)` succeeds (no error).
    """
    ann_item = find_annotation_item(task_name, sample_id)
    if ann_item is None:
        return {"eval_ok": False, "error": f"annotation item not found: task={task_name} id={sample_id}"}

    if task_name in ["Billiards", "Paper_Folding"]:
        input_abs, target_abs = resolve_input_and_target_paths(task_name, ann_item)
        if not os.path.exists(input_abs):
            return {"eval_ok": False, "error": f"missing source image: {input_abs}"}
        img1 = load_rgba(input_abs)
        img2 = load_rgba(target_abs)
    else:
        source_abs, layer_abs = resolve_source_and_layer_paths(task_name, ann_item)
        if not os.path.exists(source_abs):
            return {"eval_ok": False, "error": f"missing source image: {source_abs}"}

        img1 = load_rgba(source_abs)
        # For Pose_Control: img2 should be the instruction image itself (not merged)
        if task_name == "Pose_Control":
            if layer_abs and os.path.exists(layer_abs):
                img2 = load_rgba(layer_abs)
                # optional: align size to source if needed
                if img2.size != img1.size:
                    img2 = img2.resize(img1.size, resample=Image.BICUBIC)
            else:
                # fallback: if instruction image missing, keep pipeline running
                img2 = Image.new("RGBA", img1.size, (0, 0, 0, 0))
                print(f"[WARN] Missing instruction image for Pose_Control: {layer_abs}")
        else:
            img2 = merge_source_and_layer(source_abs, layer_abs)

    if os.path.exists(gen_image_abs):
        img3 = load_rgba(gen_image_abs)
    else:
        # keep pipeline running; still call GPT with blank image
        img3 = Image.new("RGBA", img1.size, (0, 0, 0, 0))

    base_prompt = read_text(prompt_txt_path).strip()
    base_prompt = maybe_modify_visual_coherence_prompt(task_name, metric_name or "", base_prompt)
    user_prompt = base_prompt
    if per_item_input_prompt:
        # allow prompt template: replace {prompt}
        user_prompt = user_prompt.replace("{prompt}", per_item_input_prompt)

    client = make_client()
    deployment = get_deployment_name()

    if metric_name in USE_LAST_TWO_IMAGES_METRICS:
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {"type": "image_url", "image_url": {"url": pil_to_data_url(img2)},"detail": "high"},
                    {"type": "image_url", "image_url": {"url": pil_to_data_url(img3)},"detail": "high"},
                ],
            }
        ]
    elif metric_name in USE_FIRST_AND_LAST_IMAGES_METRICS:
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {"type": "image_url", "image_url": {"url": pil_to_data_url(img1)},"detail": "high"},
                    {"type": "image_url", "image_url": {"url": pil_to_data_url(img3)},"detail": "high"},
                ],
            }
        ]
    else:
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {"type": "image_url", "image_url": {"url": pil_to_data_url(img1)},"detail": "high"},
                    {"type": "image_url", "image_url": {"url": pil_to_data_url(img2)},"detail": "high"},
                    {"type": "image_url", "image_url": {"url": pil_to_data_url(img3)},"detail": "high"},
                ],
            }
        ]

    parse_fn = getattr(metric_spec, "parse_fn", None)

    text = ""
    parsed_ok = False
    parse_error: Optional[str] = None
    metric_payload: Optional[Dict[str, Any]] = None
    metric_score: Optional[float] = None

    success = False
    i = 0
    while not success:
        if i > 50:
            raise RuntimeError(f"API call failed after {i} retries")
        try:
            resp = client.chat.completions.create(model=deployment, messages=messages)
            text = resp.choices[0].message.content or ""

            if parse_fn is not None:
                i += 1
                payload, score, err = parse_fn(text)
                if err is None and isinstance(payload, dict):
                    parsed_ok = True
                    parse_error = None
                    metric_payload = payload
                    metric_score = score
                    success = True
                else:
                    parsed_ok = False
                    parse_error = err or "parse_fn returned invalid payload"
                    # 继续 while，重新请求API
            else:
                # no parse gate, just return
                success = True

        except openai.RateLimitError as e:
            print(f"RateLimitError occurred: {e}")
            i += 1
            if hasattr(e, "status_code") and e.status_code == 429:
                time.sleep(5)
        except openai.PermissionDeniedError as e:
            i += 1
            print(f"PermissionDeniedError occurred: {e}")
            time.sleep(60)
        except openai.BadRequestError as e:
            i += 1
            print(f"BadRequestError occurred: {e}")
            if hasattr(e, "status_code") and e.status_code == 400:
                time.sleep(5)
        except openai.InternalServerError as e:
            i += 1
            print(f"InternalServerError occurred: {e}")
            time.sleep(60)
        except openai.APIConnectionError as e:
            i += 1
            print(f"APIConnectionError occurred: {e}")
            time.sleep(60)

    out: Dict[str, Any] = {
        "eval_ok": True,
        "gpt_text": text,
        "parsed_ok": parsed_ok,
        "parse_error": parse_error,
    }

    if metric_spec is not None:
        out.update({
            "metric_name": getattr(metric_spec, "name", metric_name),
            "metric_payload": metric_payload,
            "metric_score": metric_score,
        })

    return out
