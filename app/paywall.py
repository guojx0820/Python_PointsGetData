from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PlanConfig:
    monthly_limit: int


PLAN_LIMITS: dict[str, PlanConfig] = {
    "free": PlanConfig(monthly_limit=10),
    "pro": PlanConfig(monthly_limit=300),
    "lab": PlanConfig(monthly_limit=5000),
}


class UsageTracker:
    """演示版内存计数器：生产环境请换 Redis/DB。"""

    def __init__(self) -> None:
        self._usage: dict[str, int] = {}

    def check_and_consume(self, api_key: str, plan: str) -> tuple[bool, int, int]:
        cfg = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])
        used = self._usage.get(api_key, 0)
        if used >= cfg.monthly_limit:
            return False, used, cfg.monthly_limit

        used += 1
        self._usage[api_key] = used
        return True, used, cfg.monthly_limit
