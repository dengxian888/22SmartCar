from __future__ import annotations
import threading
import time

class TaskNode:
    def __init__(self, name, params, ctx):
        self.name = name
        self.params = params
        self.ctx = ctx
        self._cancelled = False
        self._mock_seq = self.params.get("_mock")
        self._mock_idx = 0
        self._mock_lock = threading.Lock()

    def setup(self): pass
    def execute(self) -> str: raise NotImplementedError
    def cancel(self): self._cancelled = True
    def teardown(self): pass

    def _mock(self):
        m = self._mock_seq
        if m is None: return None
        if isinstance(m, str): return m
        if isinstance(m, list):
            if not m: return None
            with self._mock_lock:
                idx = min(self._mock_idx, len(m) - 1)
                self._mock_idx += 1
                return m[idx]
        return None

    def _mock_sleep(self, seconds: float):
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            if self._cancelled: return
            time.sleep(0.01)

class WaitForTrigger(TaskNode):
    def execute(self):
        after = self.params.get("_mock_trigger_after")
        if after is not None:
            self._mock_sleep(after)
            return "CANCELLED" if self._cancelled else "SUCCESS"
        return "FAILED"

class NavigateTo(TaskNode):
    def execute(self):
        pose = self.params.get("pose")
        if pose is None and self.params.get("pose_from_context"):
            pose = self.ctx.data.get(self.params["pose_from_context"])
        if pose is None: return "FAILED"
        
        sleep_s = self.params.get("_mock_sleep")
        if sleep_s: self._mock_sleep(sleep_s)
        if self._cancelled: return "CANCELLED"
        
        if self._mock() == "fail": return "FAILED"
        self.ctx.data["last_nav_result"] = pose
        return "SUCCESS"

class DetectTarget(TaskNode):
    def execute(self):
        if self._mock() == "fail": return "FAILED"
        target = {"id": "qr_01", "confidence": 0.9}
        if target["confidence"] < self.params.get("min_confidence", 0.7): return "FAILED"
        self.ctx.data["target_pose"] = target
        self.ctx.data["target_id"] = target["id"]
        return "SUCCESS"

class ExecuteGrasp(TaskNode):
    def execute(self):
        if self._mock() == "fail": return "FAILED"
        self.ctx.data["grasp_result"] = "ok"
        return "SUCCESS"

class SpeakTTS(TaskNode):
    def execute(self):
        from .logger import Logger
        Logger.info(f"TTS 播报: {self.params.get('text', '')}")
        return "SUCCESS"