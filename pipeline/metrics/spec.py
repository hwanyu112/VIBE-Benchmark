from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Tuple

ParseFn = Callable[[str], Tuple[Optional[Dict[str, Any]], Optional[float], Optional[str]]]

@dataclass
class MetricSpec:
    name: str
    prompt_txt_path: str
    parse_fn: ParseFn

    def is_already_done(self, item: Dict[str, Any]) -> bool:
        if self.name not in item:
            return False
        v = item.get(self.name)
        return isinstance(v, dict) and ("score" in v)
