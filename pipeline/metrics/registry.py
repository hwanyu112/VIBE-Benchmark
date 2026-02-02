from typing import Any, Dict, List, Optional, Tuple

from ..parsing import loads_json_object
from .spec import MetricSpec

IA_KEYS = [
    "Visual_Instruction_Localization_Correctness",
    "Visual_Operator_Type_Compliance",
    "Textual_Action_Semantic_Compliance",
]

POSE_KEYS = [
    "Left_Arm",
    "Right_Arm",
    "Left_Leg",
    "Right_Leg",
]

VALID_VALUES = {"MATCH", "MISMATCH", "N/A"}

VC_KEYS = [
    "Style_Consistency",
    "Visual_Seamlessness",
    "Artifact-Free_Generation",
]

BII_CIC_CP_KEYS = [
    "Body Instance Integrity",
    "Character Identity Consistency",
    "Context Preservation",
]

LDC_KEYS = [
    "Direction_Matching_Consistency",
    "Physical_Lighting_Consistency"
]

WCP_KEYS = [
    "Wind-Identity_Preservation",
    "Wind-Other_Preservation"
]

OA_KEYS = [
    "Yaw",
    "Pitch",
    "Roll"
]

RCP_KEYS = [
    "Identity_Consistency",
    "Visual_Integrity"
]

BILLIARDS_KEYS = [
    "Context_Preservation",
    "Path_Correctness",
    "Collision_Correctness"
]

PAPER_FOLDING_KEYS = [
    "Folded_Shape_Consistency",
    "Paper_Identity_Preservation",
    "Visual_Cleanliness"
]

def parse_billiards(text: str) -> Tuple[Optional[Dict[str, Any]], Optional[float], Optional[str]]:
    try:
        obj = loads_json_object(text)
    except Exception as e:
        return None, None, f"JSON parse failed: {e}"

    missing = [k for k in BILLIARDS_KEYS if k not in obj]
    if missing:
        return None, None, f"Missing keys: {missing}"

    payload: Dict[str, Any] = {}
    scores: Dict[str, float] = {}
    for k in BILLIARDS_KEYS:
        v = obj.get(k)
        if not isinstance(v, dict):
            return None, None, f"{k} is not an object."
        reason = v.get("reason", "")
        score = v.get("score")
        try:
            score_i = float(score)
        except Exception:
            return None, None, f"{k} score is not float-castable."
        if score_i not in (0, 1):
            return None, None, f"{k} score must be 0/1."
        payload[k] = {"reason": str(reason), "score": score_i}
        scores[k] = score_i

    # Score = Context_Preservation * (Path_Correctness + Collision_Correctness) / 2
    cp = scores["Context_Preservation"]
    pc = scores["Path_Correctness"]
    cc = scores["Collision_Correctness"]
    
    s = round(cp * (pc + cc) / 2.0 + 1e-12, 4)
    payload["score"] = s
    return payload, float(s), None

def parse_wind_contextual_preservation(text: str) -> Tuple[Optional[Dict[str, Any]], Optional[float], Optional[str]]:
    try:
        obj = loads_json_object(text)
    except Exception as e:
        return None, None, f"JSON parse failed: {e}"

    missing = [k for k in WCP_KEYS if k not in obj]
    if missing:
        return None, None, f"Missing keys: {missing}"

    payload: Dict[str, Any] = {}
    total = 0.0
    for k in WCP_KEYS:
        v = obj.get(k)
        if not isinstance(v, dict):
            return None, None, f"{k} is not an object."
        reason = v.get("reason", "")
        score = v.get("score")
        try:
            score_i = float(score)
        except Exception:
            return None, None, f"{k} score is not float-castable."
        if score_i not in (0, 1, 0.5):
            return None, None, f"{k} score must be 0/1/0.5."
        payload[k] = {"reason": str(reason), "score": score_i}
        total += float(score_i)

    s = round(total / 2.0 + 1e-12, 4)
    payload["score"] = s
    return payload, float(s), None

def parse_reorientation_contextual_preservation(text: str) -> Tuple[Optional[Dict[str, Any]], Optional[float], Optional[str]]:
    try:
        obj = loads_json_object(text)
    except Exception as e:
        return None, None, f"JSON parse failed: {e}"

    missing = [k for k in RCP_KEYS if k not in obj]
    if missing:
        return None, None, f"Missing keys: {missing}"

    payload: Dict[str, Any] = {}
    total = 0.0
    for k in RCP_KEYS:
        v = obj.get(k)
        if not isinstance(v, dict):
            return None, None, f"{k} is not an object."
        reason = v.get("reason", "")
        score = v.get("score")
        try:
            score_i = float(score)
        except Exception:
            return None, None, f"{k} score is not float-castable."
        if score_i not in (0, 1, 0.5):
            return None, None, f"{k} score must be 0/1/0.5."
        payload[k] = {"reason": str(reason), "score": score_i}
        total += float(score_i)

    s = round(total / 2.0 + 1e-12, 4)
    payload["score"] = s
    return payload, float(s), None

def parse_light_direction_consistency(text: str) -> Tuple[Optional[Dict[str, Any]], Optional[float], Optional[str]]:
    try:
        obj = loads_json_object(text)
    except Exception as e:
        return None, None, f"JSON parse failed: {e}"

    missing = [k for k in LDC_KEYS if k not in obj]
    if missing:
        return None, None, f"Missing keys: {missing}"

    payload: Dict[str, Any] = {}
    total = 0.0
    for k in LDC_KEYS:
        v = obj.get(k)
        if not isinstance(v, dict):
            return None, None, f"{k} is not an object."
        reason = v.get("reason", "")
        score = v.get("score")
        try:
            score_i = float(score)
        except Exception:
            return None, None, f"{k} score is not float-castable."
        if score_i not in (0, 1):
            return None, None, f"{k} score must be 0/1."
        payload[k] = {"reason": str(reason), "score": score_i}
        total += float(score_i)

    s = round(total / 2.0 + 1e-12, 4)
    payload["score"] = s
    return payload, float(s), None

def parse_pose_consistency(text: str) -> Tuple[Optional[Dict[str, Any]], Optional[float], Optional[str]]:
    try:
        obj = loads_json_object(text)
    except Exception as e:
        return None, None, f"JSON parse failed: {e}"

    if "Pose_Consistency" not in obj:
        return None, None, "Missing key: Pose_Consistency"

    pc = obj["Pose_Consistency"]
    if not isinstance(pc, dict):
        return None, None, "Pose_Consistency is not an object."

    payload: Dict[str, Any] = {}
    match_cnt = 0
    eval_cnt = 0  # MATCH + MISMATCH only

    for k in POSE_KEYS:
        if k not in pc:
            return None, None, f"Missing key: {k}"

        v = pc.get(k)
        if not isinstance(v, str):
            return None, None, f"{k} must be a string."

        v_clean = v.strip()
        if v_clean not in VALID_VALUES:
            return None, None, f"{k} must be one of {sorted(VALID_VALUES)}, got: {v_clean}"

        payload[k] = v_clean

        if v_clean in ("MATCH", "MISMATCH"):
            eval_cnt += 1
            if v_clean == "MATCH":
                match_cnt += 1

    # score computation
    if eval_cnt == 0:
        score = 0.0
    else:
        score = round(match_cnt / eval_cnt + 1e-12, 4)

    payload["score"] = score
    return payload, score, None

def parse_orientation_alignment(text: str) -> Tuple[Optional[Dict[str, Any]], Optional[float], Optional[str]]:
    try:
        obj = loads_json_object(text)
    except Exception as e:
        return None, None, f"JSON parse failed: {e}"

    missing = [k for k in OA_KEYS if k not in obj]
    if missing:
        return None, None, f"Missing keys: {missing}"

    payload: Dict[str, Any] = {}
    total = 0.0
    count = 0  # 计数需要修改的元素
    
    for k in OA_KEYS:
        v = obj.get(k)
        if not isinstance(v, dict):
            return None, None, f"{k} is not an object."
        
        reason = v.get("reason", "")
        score = v.get("score")
        needs_modification = v.get("needs_modification")
        
        # 验证 needs_modification
        if not isinstance(needs_modification, bool):
            return None, None, f"{k} needs_modification is not a boolean."
        
        try:
            score_i = int(score)
        except Exception:
            return None, None, f"{k} score is not int-castable."
        if score_i not in (0, 1):
            return None, None, f"{k} score must be 0/1."
        
        payload[k] = {"reason": str(reason), "score": score_i, "needs_modification": needs_modification}
        
        # 只计算 needs_modification 为 true 的元素
        if needs_modification:
            total += float(score_i)
            count += 1

    # 计算分数：如果所有 needs_modification 都为 false，则总分为 0
    if count == 0:
        s = 0.0
    else:
        s = round(total / count + 1e-12, 4)
    
    payload["score"] = s
    return payload, float(s), None

def parse_visual_coherence(text: str) -> Tuple[Optional[Dict[str, Any]], Optional[float], Optional[str]]:
    try:
        obj = loads_json_object(text)
    except Exception as e:
        return None, None, f"JSON parse failed: {e}"

    missing = [k for k in VC_KEYS if k not in obj]
    if missing:
        return None, None, f"Missing keys: {missing}"

    payload: Dict[str, Any] = {}
    total = 0.0
    for k in VC_KEYS:
        v = obj.get(k)
        if not isinstance(v, dict):
            return None, None, f"{k} is not an object."
        reason = v.get("reason", "")
        score = v.get("score")
        try:
            score_i = int(score)
        except Exception:
            return None, None, f"{k} score is not int-castable."
        if score_i not in (0, 1):
            return None, None, f"{k} score must be 0/1."
        payload[k] = {"reason": str(reason), "score": score_i}
        total += float(score_i)

    s = round(total / 3.0 + 1e-12, 4)
    payload["score"] = s
    return payload, float(s), None

def parse_instruction_adherence(text: str) -> Tuple[Optional[Dict[str, Any]], Optional[float], Optional[str]]:
    try:
        obj = loads_json_object(text)
    except Exception as e:
        return None, None, f"JSON parse failed: {e}"

    missing = [k for k in IA_KEYS if k not in obj]
    if missing:
        return None, None, f"Missing keys: {missing}"

    payload: Dict[str, Any] = {}
    total = 0.0
    for k in IA_KEYS:
        v = obj.get(k)
        if not isinstance(v, dict):
            return None, None, f"{k} is not an object."
        reason = v.get("reason", "")
        score = v.get("score")
        try:
            score_i = float(score)
        except Exception:
            return None, None, f"{k} score is not float-castable."
        if score_i not in (0, 0.5, 1):
            return None, None, f"{k} score must be 0/0.5/1."
        payload[k] = {"reason": str(reason), "score": score_i}
        total += float(score_i)

    s = round(total / 3.0 + 1e-12, 4)
    payload["score"] = s
    return payload, float(s), None

def parse_BII_CIC_CP(text: str) -> Tuple[Optional[Dict[str, Any]], Optional[float], Optional[str]]:
    try:
        obj = loads_json_object(text)
    except Exception as e:
        return None, None, f"JSON parse failed: {e}"

    missing = [k for k in BII_CIC_CP_KEYS if k not in obj]
    if missing:
        return None, None, f"Missing keys: {missing}"

    payload: Dict[str, Any] = {}
    total = 0.0
    for k in BII_CIC_CP_KEYS:
        v = obj.get(k)
        if not isinstance(v, dict):
            return None, None, f"{k} is not an object."
        reason = v.get("reason", "")
        score = v.get("score")
        try:
            score_i = int(score)
        except Exception:
            return None, None, f"{k} score is not int-castable."
        if score_i not in (0, 1):
            return None, None, f"{k} score must be 0/1."
        payload[k] = {"reason": str(reason), "score": score_i}
        total += float(score_i)

    s = round(total / 3.0 + 1e-12, 4)
    payload["score"] = s
    return payload, float(s), None

def parse_single_metric_wrapped(metric_name: str, text: str) -> Tuple[Optional[Dict[str, Any]], Optional[float], Optional[str]]:
    try:
        obj = loads_json_object(text)
    except Exception as e:
        return None, None, f"JSON parse failed: {e}"

    if metric_name not in obj:
        return None, None, f"Missing key: {metric_name}"

    v = obj.get(metric_name)
    if not isinstance(v, dict):
        return None, None, f"{metric_name} is not an object."

    reason = v.get("reason", "")
    score = v.get("score")
    try:
        score_i = float(score)
    except Exception:
        return None, None, f"{metric_name} score is not float-castable."
    if score_i not in (0, 0.5, 1):
        return None, None, f"{metric_name} score must be 0/0.5/1."

    payload = {"reason": str(reason), "score": score_i}
    return payload, float(score_i), None

def build_metric_specs(metric_prompts: Dict[str, str]) -> List[MetricSpec]:
    specs: List[MetricSpec] = []
    for name, prompt_path in metric_prompts.items():
        if name == "Instruction_Adherence":
            specs.append(MetricSpec(name=name, prompt_txt_path=prompt_path, parse_fn=parse_instruction_adherence))
        elif name == "Pose_Consistency":
            specs.append(MetricSpec(name=name, prompt_txt_path=prompt_path, parse_fn=parse_pose_consistency))
        elif name == "BII_CIC_CP":
            specs.append(MetricSpec(name=name, prompt_txt_path=prompt_path, parse_fn=parse_BII_CIC_CP))
        elif name == "Visual_Coherence":
            specs.append(MetricSpec(name=name, prompt_txt_path=prompt_path, parse_fn=parse_visual_coherence))
        elif name == "Light_Direction_Consistency":
            specs.append(MetricSpec(name=name, prompt_txt_path=prompt_path, parse_fn=parse_light_direction_consistency))
        elif name == "Wind_Contextual_Preservation":
            specs.append(MetricSpec(name=name, prompt_txt_path=prompt_path, parse_fn=parse_wind_contextual_preservation))
        elif name == "Orientation_Alignment":
            specs.append(MetricSpec(name=name, prompt_txt_path=prompt_path, parse_fn=parse_orientation_alignment))
        elif name == "Reorientation_Contextual_Preservation":
            specs.append(MetricSpec(name=name, prompt_txt_path=prompt_path, parse_fn=parse_reorientation_contextual_preservation))
        elif name == "Billiards":
            specs.append(MetricSpec(name=name, prompt_txt_path=prompt_path, parse_fn=parse_billiards))
        else:
            specs.append(MetricSpec(
                name=name,
                prompt_txt_path=prompt_path,
                parse_fn=lambda text, _n=name: parse_single_metric_wrapped(_n, text),
            ))
    return specs
