import json
import re
from typing import Any, Dict, Optional

def extract_json_candidate(text: str) -> Optional[str]:
    t = (text or "").strip()

    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", t, flags=re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()

    first_open = text.find("{")
    last_close = text.rfind("}")
    if first_open == -1 or last_close == -1 or last_close < first_open:
        return None
    candidate = text[first_open:last_close+1].strip()
    # quick sanity
    if len(candidate) < 2:
        return None
    return candidate

def loads_json_object(text: str) -> Dict[str, Any]:
    cand = extract_json_candidate(text)
    if not cand:
        raise ValueError("No JSON object found in response.")
    obj = json.loads(cand)
    if not isinstance(obj, dict):
        raise ValueError("Parsed JSON is not an object.")
    return obj
