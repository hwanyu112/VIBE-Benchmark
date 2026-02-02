import argparse
import os
import math
import shutil
import json
from typing import Any, Dict, List, Optional

from tqdm import tqdm

from .io_utils import read_json, write_json
from .scoring import compute_summary
from .evaluator import evaluate_one
from .metrics.registry import build_metric_specs


def resolve_gen_abs(gen_prefix: str, saved_image_path: str) -> str:
    """
    Resolve absolute path for generated image.

    Priority:
    1) gen_prefix / saved_image_path
    2) gen_prefix / imgs / saved_image_path   (fallback for missing 'imgs/' prefix)
    3) return primary path anyway, but print warning if neither exists
    """
    # primary path (expected)
    p1 = os.path.normpath(os.path.join(gen_prefix, saved_image_path))
    if os.path.exists(p1):
        return p1

    # fallback: missing 'imgs/' prefix
    p2 = os.path.normpath(os.path.join(gen_prefix, "imgs", saved_image_path))
    if os.path.exists(p2):
        return p2

    # neither exists: keep original behavior but warn
    print(f"[WARN] Generated image not found: {p1} (also tried {p2})")
    return p1

def _collect_all_scores(payload: Any, metric_name: str, target_dict: Dict[str, List[float]]) -> None:
    """
    Collect all scores from a metric payload.
    Includes the top-level 'score' and any nested 'score' fields in sub-dictionaries.
    """
    if not isinstance(payload, dict):
        return
    
    # 1. Top-level score
    if "score" in payload:
        try:
            s = float(payload["score"])
            target_dict.setdefault(metric_name, []).append(s)
        except (ValueError, TypeError):
            pass
            
    # 2. Sub-metrics (e.g., Billiards/Context_Preservation)
    for k, v in payload.items():
        if k == "score":
            continue
        if isinstance(v, dict) and "score" in v:
            try:
                sub_score = float(v["score"])
                sub_key = f"{metric_name}/{k}"
                target_dict.setdefault(sub_key, []).append(sub_score)
            except (ValueError, TypeError):
                pass

def get_metric_score(item: Dict[str, Any], metric_name: str) -> Optional[float]:
    v = item.get(metric_name)
    if not isinstance(v, dict):
        return None
    if "score" not in v:
        return None
    try:
        return float(v["score"])
    except Exception:
        return None


def update_overall_score_geomean(item: Dict[str, Any]) -> None:
    """
    Compute item['score'] as geometric mean over ALL metrics currently present in the item
    (any dict field that has a numeric 'score'), excluding the top-level 'score' itself.
    If any metric score is 0 -> geometric mean becomes 0.
    """
    scores: List[float] = []
    for k, v in item.items():
        if k == "score":
            continue
        if isinstance(v, dict) and ("score" in v):
            try:
                s = float(v["score"])
            except Exception:
                continue
            # 只接受 [0,1] 范围；不在范围就忽略（或你也可以直接报错）
            if 0.0 <= s <= 1.0:
                scores.append(s)

    if not scores:
        return  # 没有任何metric分数就不写总分

    if any(s <= 0.0 for s in scores):
        item["score"] = 0.0
        return

    gm = math.exp(sum(math.log(s) for s in scores) / len(scores))
    item["score"] = round(gm + 1e-12, 4)

def _parse_prompts(kvs: List[str]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for kv in kvs:
        if "=" not in kv:
            raise ValueError(f"Invalid --prompt: {kv}. Use MetricName=/path/to/prompt.txt")
        k, v = kv.split("=", 1)
        k = k.strip()
        v = v.strip()
        if not k or not v:
            raise ValueError(f"Invalid --prompt: {kv}.")
        out[k] = v
    return out

def _add_suffix_json(path: str, idx: int) -> str:
    root, ext = os.path.splitext(path)
    return f"{root}_{idx}{ext}"

def aggregate_run_summaries(run_summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Input: list of summary_i.json dicts (already percentage values, e.g. 43.21)
    Output: {"n": N, "mean": {...}, "var": {...}}
    Variance uses sample variance (divide by n-1) when n>1, else 0.0
    """
    keys = set()
    for s in run_summaries:
        keys.update(s.keys())

    out_mean: Dict[str, Any] = {}
    out_var: Dict[str, Any] = {}

    n = len(run_summaries)
    for k in sorted(keys):
        vals: List[float] = []
        for s in run_summaries:
            v = s.get(k)
            if isinstance(v, (int, float)):
                vals.append(float(v))

        if not vals:
            out_mean[k] = None
            out_var[k] = None
            continue

        mu = sum(vals) / len(vals)
        if len(vals) > 1:
            var = sum((x - mu) ** 2 for x in vals) / (len(vals) - 1)  # sample variance
        else:
            var = 0.0

        out_mean[k] = round(mu + 1e-12, 2)
        out_var[k] = round(var + 1e-12, 4)

    return {"n": n, "mean": out_mean, "var": out_var}

def process_one_result_json(
    result_json_path: str,
    metric_specs: List[Any],
    gen_prefix: str,
    task_name: str,
    rerun: bool,
) -> None:
    data = read_json(result_json_path)
    if not isinstance(data, list):
        raise ValueError(f"Result json must be a list: {result_json_path}")

    # Summary:
    # - overall mean of per-sample item["score"]
    # - mean of each metric's per-sample score
    overall_scores: List[float] = []
    metric_success_scores: Dict[str, List[float]] = {spec.name: [] for spec in metric_specs}

    for item in tqdm(data, desc=f"{task_name}"):
        if item.get("status") != "success":
            continue

        sample_id = str(item.get("id"))
        saved_image_path = str(item.get("saved_image_path"))
        gen_abs = resolve_gen_abs(gen_prefix, saved_image_path)

        for spec in metric_specs:
            mname = spec.name

            # --- Visual_Coherence gating ---
            if mname == "Visual_Coherence":
                ia_score = get_metric_score(item, "Instruction_Adherence")
                if ia_score == 0:
                    item["Visual_Coherence"] = {
                        "reason": "Skipped because Instruction_Adherence.score == 0",
                        "score": 0,
                    }
                    # record metric score for summary
                    _collect_all_scores(item[mname], mname, metric_success_scores)

                    # update overall
                    update_overall_score_geomean(item)
                    write_json(result_json_path, data)
                    continue

            # Resume / skip per metric unless rerun
            if (not rerun) and spec.is_already_done(item):
                # collect existing metric score
                _collect_all_scores(item[mname], mname, metric_success_scores)
                # keep overall updated
                update_overall_score_geomean(item)
                write_json(result_json_path, data)
                continue

            eval_out = evaluate_one(
                task_name=task_name,
                sample_id=sample_id,
                prompt_txt_path=spec.prompt_txt_path,
                gen_image_abs=gen_abs,
                per_item_input_prompt=item.get("input_prompt"),
                metric_name=mname,
                metric_spec=spec,
            )

            if not eval_out.get("eval_ok"):
                item.setdefault("_eval_errors", [])
                item["_eval_errors"].append(eval_out.get("error", "unknown eval error"))
                write_json(result_json_path, data)
                continue

            payload = eval_out.get("metric_payload")
            score = eval_out.get("metric_score")
            parse_error = eval_out.get("parse_error")

            if isinstance(payload, dict):
                if "score" not in payload and score is not None:
                    payload["score"] = score
                item[mname] = payload

                # collect metric score for summary
                _collect_all_scores(payload, mname, metric_success_scores)
            else:
                item[mname] = {
                    "error": parse_error or "missing payload",
                    "raw": eval_out.get("gpt_text", ""),
                }

            # update overall
            update_overall_score_geomean(item)
            write_json(result_json_path, data)

        # collect overall for summary (after finishing metrics for this sample)
        if "score" in item:
            try:
                overall_scores.append(float(item["score"]))
            except Exception:
                pass

    write_json(result_json_path, data)

    summary_path = os.path.join(os.path.dirname(result_json_path), f"{task_name}_summary.json")
    summary_obj: Dict[str, Any] = {}

    # overall mean
    summary_obj["score"] = round(sum(overall_scores) / len(overall_scores) * 100.0 + 1e-12, 2) if overall_scores else None

    # per-metric mean (including sub-metrics)
    for mname in sorted(metric_success_scores.keys()):
        vals = metric_success_scores[mname]
        summary_obj[mname] = round(sum(vals) / len(vals) * 100.0 + 1e-12, 2) if vals else None

    write_json(summary_path, summary_obj)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", action="append", required=True, help="MetricName=/path/to/prompt.txt (repeatable).")
    ap.add_argument("--gen_prefix", required=True, help="Prefix directory for generated images.")
    ap.add_argument("--result_json", action="append", default=[], help="Path to a task result json. Can be repeated.")
    ap.add_argument("--results_root", default=None, help="Folder containing many task jsons.")
    ap.add_argument("--task_name", required=True, help="Task name for evaluation (must exist in TASK_CONFIG).")
    ap.add_argument("--repeat", type=int, default=1, help="Repeat evaluation N times and aggregate mean/variance.")
    ap.add_argument("--repeat_resume", action="store_true",
                help="If set, each repeat run will resume from existing *_i.json instead of overwriting from the base file.")
    args = ap.parse_args()

    metric_prompts = _parse_prompts(args.prompt)
    metric_specs = build_metric_specs(metric_prompts)

    result_files: List[str] = []
    if args.result_json:
        result_files.extend(args.result_json)
    elif args.results_root:
        for fn in os.listdir(args.results_root):
            if fn.endswith(".json"):
                result_files.append(os.path.join(args.results_root, fn))
    else:
        raise ValueError("Provide --result_json (one or many) or --results_root")

    for p in result_files:
        print(f"Processing result json: {p}")

        repeat_n = max(1, int(args.repeat))

        with open(p, "r", encoding="utf-8") as f:
            base_data = json.load(f)

        run_summaries: List[Dict[str, Any]] = []

        for i in range(1, repeat_n + 1):
            run_json_path = _add_suffix_json(p, i)  # source_i.json
            run_summary_path = os.path.join(os.path.dirname(run_json_path), f"{args.task_name}_summary_{i}.json")

            if args.repeat_resume:
                if not os.path.exists(run_json_path):
                    with open(run_json_path, "w", encoding="utf-8") as f:
                        json.dump(base_data, f, ensure_ascii=False, indent=2)
                rerun_flag = False  
            else:
                with open(run_json_path, "w", encoding="utf-8") as f:
                    json.dump(base_data, f, ensure_ascii=False, indent=2)
                rerun_flag = True

            process_one_result_json(
                result_json_path=run_json_path,
                metric_specs=metric_specs,
                gen_prefix=args.gen_prefix,
                task_name=args.task_name,
                rerun=rerun_flag,
            )
            default_summary_path = os.path.join(os.path.dirname(run_json_path), f"{args.task_name}_summary.json")
            if os.path.exists(default_summary_path):
                shutil.move(default_summary_path, run_summary_path)
            else:
                with open(run_summary_path, "w", encoding="utf-8") as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)

            with open(run_summary_path, "r", encoding="utf-8") as f:
                run_summaries.append(json.load(f))

        final_summary_path = os.path.join(os.path.dirname(p), f"{args.task_name}_summary.json")
        agg = aggregate_run_summaries(run_summaries)
        with open(final_summary_path, "w", encoding="utf-8") as f:
            json.dump(agg, f, ensure_ascii=False, indent=2)

        print(f"[DONE] Wrote aggregated summary: {final_summary_path}")


if __name__ == "__main__":
    main()
