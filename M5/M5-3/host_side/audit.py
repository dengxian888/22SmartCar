import json, hashlib, time
from pathlib import Path

class AuditLogger:
    def __init__(self, log_dir="."):
        date_str = time.strftime("%Y%m%d")
        self.log_path = Path(log_dir) / f"audit_log_{date_str}.jsonl"
        self.prev_hash = ""
        self.anchor_path = Path(log_dir) / f"audit_anchor_{date_str}.txt" # 新增：外部锚点文件
        self._ensure_file()

    def _ensure_file(self):
        # 续接昨天的哈希链（如果有）
        if self.log_path.exists():
            with open(self.log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if lines:
                    self.prev_hash = json.loads(lines[-1]).get("hash", "")
        else:
            self.log_path.touch()

    def _calc_hash(self, record: dict) -> str:
        record_copy = {k: v for k, v in record.items() if k != "hash"}
        raw = json.dumps(record_copy, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def log(self, op: str, source: str, user: str = "operator", **kwargs):
        ts = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()) + f".{int(time.time()*1000)%1000:03d}"
        record = {
            "ts": ts,
            "op": op,
            "source": source,
            "user": user,
            "prev_hash": self.prev_hash,
            **kwargs
        }
        record["hash"] = self._calc_hash(record)
        
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        
        self.prev_hash = record["hash"]
        self.anchor_path.write_text(self.prev_hash)
        return record