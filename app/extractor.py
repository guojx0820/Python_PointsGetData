from __future__ import annotations

import re
from typing import Iterable

from .models import ExtractedMetric


PATTERNS: dict[str, str] = {
    "temperature": r"(?P<value>\d+(?:\.\d+)?)\s?(?P<unit>°C|C|K)",
    "cycle_life": r"(?P<value>\d{2,5})\s?(?P<unit>cycles?)",
    "coulombic_efficiency": r"(?P<value>\d+(?:\.\d+)?)\s?(?P<unit>%)\s?(?:CE|coulombic efficiency)?",
    "capacity": r"(?P<value>\d+(?:\.\d+)?)\s?(?P<unit>mAh/g|mAh g-1|Ah/kg)",
    "voltage": r"(?P<value>\d+(?:\.\d+)?)\s?(?P<unit>V)",
}


def extract_metrics(text: str) -> list[ExtractedMetric]:
    found: list[ExtractedMetric] = []
    for metric, pattern in PATTERNS.items():
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            value = match.group("value")
            unit = match.groupdict().get("unit")
            found.append(ExtractedMetric(metric=metric, value=value, unit=unit))

    # 去重，保留前 50 条
    unique: dict[tuple[str, str, str | None], ExtractedMetric] = {}
    for item in found:
        unique[(item.metric, item.value, item.unit)] = item
    return list(unique.values())[:50]


def build_abstract(text: str, max_chars: int = 500) -> str:
    lines: Iterable[str] = [line.strip() for line in text.splitlines() if line.strip()]
    joined = " ".join(lines)
    if len(joined) <= max_chars:
        return joined
    return joined[: max_chars - 3] + "..."
