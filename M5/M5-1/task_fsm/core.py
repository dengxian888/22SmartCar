from __future__ import annotations
import threading, time, yaml, json
from datetime import datetime, timezone
from .context import TaskContext
from .registry import NODE_REGISTRY
from .logger import Logger

class TaskEngine:
    def __init__(self, yaml_path: str, ctx: TaskContext | None = None):
        self.ctx = ctx or TaskContext(task_id=f"run_{int(time.time())}")
        self.top_defs = self._read_yaml(yaml_path)
        self.defs, self.steps, self.executed = {}, [], set()
        self._collect_defs(self.top_defs)

    def _read_yaml(self, path):
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f).get("tasks", [])

    def _collect_defs(self, defs_list):
        for t in defs_list:
            name = t.get("name")
            if not name or name in self.defs: raise ValueError("节点名缺失或重复")
            if "parallel" not in t and t.get("type") not in NODE_REGISTRY:
                raise ValueError(f"未知 type '{t.get('type')}'")
            self.defs[name] = t
            if "parallel" in t: self._collect_defs(t["parallel"].get("branches", []))

    def run(self) -> str:
        status = "SUCCESS"
        for d in self.top_defs:
            if d["name"] in self.executed: continue
            if self.ctx.abort_requested: status = "ABORTED"; break
            r = self._execute_def(d, visited=set())
            self.executed.add(d["name"])
            if r in ("FAILED", "ABORTED"): status = r; break
            if r == "SKIPPED": self.ctx.degraded = True
        self._build_report(status)
        return status

    def _execute_def(self, d: dict, visited: set) -> str:
        name = d["name"]
        if "parallel" in d: return self._run_parallel(d, visited)
        
        node = NODE_REGISTRY[d["type"]](name, d, self.ctx)
        max_retries = d.get("retry", 0)
        retry_interval = d.get("retry_interval", 0.0)
        fallback, on_fail = d.get("fallback"), d.get("on_fail", "abort")
        
        self.ctx.retry_budget.setdefault(name, max_retries)
        attempt, start = 0, time.monotonic()

        while True:
            attempt += 1
            status = self._execute_with_timeout(node, d.get("timeout"))
            if status == "SUCCESS": self._record(name, "SUCCESS", attempt, start); return "SUCCESS"
            if status == "CANCELLED": self._record(name, "ABORTED", attempt, start); return "ABORTED"

            if self.ctx.retry_budget[name] > 0:
                self.ctx.retry_budget[name] -= 1
                self.ctx.meta.setdefault("retries", {})[name] = attempt
                time.sleep(retry_interval)
                continue

            if fallback and fallback not in visited and fallback != name:
                visited.add(name)
                if fallback in self.defs:
                    self.ctx.meta.setdefault("fallback_trace", []).append((name, fallback))
                    self.executed.add(fallback)
                    if self._execute_def(self.defs[fallback], visited) == "SUCCESS":
                        self._record(name, "FALLBACK_OK", attempt, start); return "SUCCESS"

            if on_fail == "skip": self.ctx.degraded = True; self._record(name, "SKIPPED", attempt, start); return "SKIPPED"
            
            self._record(name, "FAILED", attempt, start); return "FAILED"

    def _execute_with_timeout(self, node, timeout):
        box = {"status": "FAILED", "done": False}
        def _target():
            try:
                node.setup(); box["status"] = node.execute()
            finally:
                box["done"] = True; node.teardown()
        t = threading.Thread(target=_target, daemon=True); t.start(); t.join(timeout)
        if not box["done"]: node.cancel(); return "FAILED"
        return box["status"]

    def _run_parallel(self, d, visited):
        p = d["parallel"]; policy = p.get("fail_policy", "any_fail")
        results = [self._execute_def(b, visited | {d["name"]}) for b in p.get("branches", [])]
        if policy == "all_must_succeed" and any(r != "SUCCESS" for r in results): return "FAILED"
        if policy == "any_fail" and any(r == "FAILED" for r in results): return "FAILED"
        if policy == "any_success" and not any(r == "SUCCESS" for r in results): return "FAILED"
        return "SUCCESS"

    def _record(self, name, status, attempt, start):
        self.steps.append({"name": name, "status": status, "attempts": attempt, "elapsed": round(time.monotonic() - start, 3)})

    def _build_report(self, status):
        report = {"task_id": self.ctx.task_id, "status": status, "degraded": self.ctx.degraded, "finished_at": datetime.now(timezone.utc).isoformat(), "steps": self.steps, "data": self.ctx.data, "meta": self.ctx.meta}
        with open("task_report.json", "w", encoding="utf-8") as f: json.dump(report, f, ensure_ascii=False, indent=2)