import json, hashlib, sys
from pathlib import Path

def verify(log_file):
    log_path = Path(log_file)
    # 修复：先提取文件名转为字符串，再进行 replace
    anchor_name = log_path.name.replace("audit_log", "audit_anchor").replace(".jsonl", ".txt")
    anchor_path = log_path.parent / anchor_name
    
    prev_hash = ""
    last_calc_hash = ""
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                record = json.loads(line)
                if record["prev_hash"] != prev_hash:
                    print(f"❌ FAIL: 第 {i} 行哈希链断裂（被删行或被篡改）")
                    return False
                
                record_copy = {k: v for k, v in record.items() if k != "hash"}
                calc = hashlib.sha256(json.dumps(record_copy, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
                if record["hash"] != calc:
                    print(f"❌ FAIL: 第 {i} 行内容被篡改")
                    return False
                prev_hash = record["hash"]
                last_calc_hash = prev_hash
                
        # 最后一行和外部锚点比对
        if anchor_path.exists():
            anchor_hash = anchor_path.read_text().strip()
            if last_calc_hash != anchor_hash:
                print(f"❌ FAIL: 尾部删除攻击！最后一行哈希({last_calc_hash})与外部锚点({anchor_hash})不匹配。")
                return False

        print("✅ PASS: 审计日志完整，无篡改和截断痕迹。")
        return True
    except Exception as e:
        print(f"❌ FAIL: 解析异常 - {e}")
        return False

if __name__ == '__main__':
    sys.exit(0 if verify(sys.argv[1]) else 1)