import yaml
import argparse

def init_yaml():
    try:
        parser = argparse.ArgumentParser(description="我的程序") #建立参数解析
        parser.add_argument("--config", type=str, default="tasks.yaml", help="任务配置文件路径")
        parser.add_argument("--timeout", type=float, default=None, help="任务时间上限")
        parser.add_argument("--report", type=str, default="report.json", help="输出文件路径")
        parser.add_argument("--seed", type=int, default=None, help="随机种子")
        args = parser.parse_args()  #抓取命令中的参数

        TASK_PATH = args.config
        with open(TASK_PATH) as f:
            Task = yaml.safe_load(f)
            if Task is None:
                raise ValueError(f"错误：任务配置文件 '{TASK_PATH}' 为空。")
            
        timeout = args.timeout if args.timeout is not None else Task.get("timeout", 15.0)
        
        task_list = Task.get("tasks",[])
        if not task_list:
                raise ValueError("任务列表为空，请检查 YAML 文件中的'tasks'字段是否配置了任务。")

    except KeyError as e:
        raise KeyError(f"错误：task.yaml文件中缺少键 {e}")
    except FileNotFoundError:
        raise FileNotFoundError(f"任务配置文件 '{TASK_PATH}' 路径错误或不存在。")
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"YAML 语法错误！请检查缩进和格式。错误：{e}")
    return Task,timeout,task_list,args.report,args.seed
