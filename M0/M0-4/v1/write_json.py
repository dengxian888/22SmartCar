import json
def write_json(is_timeout,total_real_time,task_status,report_path):

    final_report = {
            "timeout": is_timeout, 
            "total_duration": total_real_time, 
            "tasks": []
        }

    #把 task_status 字典转成需求要求的列表格式
    for task_name, status_info in task_status.items():
            final_report["tasks"].append({
                "task_name": task_name,
                "status": status_info["status"],
                "attempt":status_info["attempt"],
                "duration":status_info["duration"],
                "started_at":status_info["started_at"],
                "ended_at":status_info["ended_at"]
            })
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(final_report, f, indent=4, ensure_ascii=False)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"{e}文件不存在")