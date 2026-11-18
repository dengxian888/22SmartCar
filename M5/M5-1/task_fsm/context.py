from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass
class TaskContext:
    task_id: str
    deadline: float | None = None
    data: dict[str, Any] = field(default_factory=dict)
    retry_budget: dict[str, int] = field(default_factory=dict)
    degraded: bool = False
    meta: dict[str, Any] = field(default_factory=dict)
    abort_requested: bool = False