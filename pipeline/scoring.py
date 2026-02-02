import json
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

REQUIRED_KEYS = [
    "Visual_Instruction_Localization_Correctness",
    "Visual_Operator_Type_Compliance",
    "Textual_Action_Semantic_Compliance",
]

@dataclass
class ParseResult:
    ok: bool
    metrics: Optional[Dict[str, Any]] = None
    score: Optional[float] = None
    error: Optional[str] = None
    raw_json_text: Optional[str] = None

def _coerce_binary(v: Any) -> Optional[int]:
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, (int, float)) and v in (0, 1):
        return int(v)
    if isinstance(v, str):
        s = v.strip()
        if s in ("0", "1"):
            return int(s)
    return None

def _extract_json_block(text: str) -> Optional[str]:
    # Prefer fenced ```json ... ```
    m = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1)

    # Otherwise: find the last {...} block by scanning braces from the end
    # This is robust for "explanation ... {json}"
    first_open = text.find("{")
    last_close = text.rfind("}")
    if first_open == -1 or last_close == -1 or last_close < first_open:
        return None
    candidate = text[first_open:last_close+1].strip()
    # quick sanity
    if len(candidate) < 2:
        return None
    return candidate

def parse_instruction_adherence(text: str) -> ParseResult:
    jtxt = _extract_json_block(text)
    if not jtxt:
        return ParseResult(ok=False, error="No JSON block found at end of response.")

    try:
        obj = json.loads(jtxt)
    except Exception as e:
        return ParseResult(ok=False, error=f"JSON parse failed: {e}", raw_json_text=jtxt)

    # Validate structure
    missing = [k for k in REQUIRED_KEYS if k not in obj]
    if missing:
        return ParseResult(ok=False, error=f"Missing keys: {missing}", metrics=obj, raw_json_text=jtxt)

    scores = []
    for k in REQUIRED_KEYS:
        entry = obj.get(k, {})
        if not isinstance(entry, dict):
            return ParseResult(ok=False, error=f"Metric '{k}' is not an object.", metrics=obj, raw_json_text=jtxt)
        s = _coerce_binary(entry.get("score"))
        if s is None:
            return ParseResult(ok=False, error=f"Metric '{k}.score' must be 0/1.", metrics=obj, raw_json_text=jtxt)
        scores.append(s)

    avg = sum(scores) / len(scores)
    avg4 = float(f"{avg:.4f}")
    return ParseResult(ok=True, metrics=obj, score=avg4, raw_json_text=jtxt)

def compute_summary(success_scores) -> float:
    # returns X already multiplied by 100 and rounded 2 decimals
    if not success_scores:
        return 0.00
    mean_score = sum(success_scores) / len(success_scores)
    x = mean_score * 100.0
    return float(f"{x:.2f}")
