import json
def write_json(is_timeout,total_real_time,task_status):

    final_report = {
            "timeout": is_timeout, 
            "total_real_time": total_real_time, 
            "tasks": []
        }

    #把 task_status 字典转成需求要求的列表格式
    for task_name, status_info in task_status.items():
            print(task_name,status_info)
            final_report["tasks"].append({
                "task_name": task_name,
                "status": status_info["status"]
            })
    try:
        with open("report.json", "w", encoding="utf-8") as f:
            json.dump(final_report, f, indent=4, ensure_ascii=False)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"{e}文件不存在")