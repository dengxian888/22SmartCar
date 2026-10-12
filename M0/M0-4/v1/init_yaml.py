import yaml
import argparse

def init_cfg():
    try:
        parser = argparse.ArgumentParser(description="我的程序") #建立参数解析
        parser.add_argument("--config", type=str, default="tasks.yaml", help="任务配置文件路径")
        args = parser.parse_args()  #抓取命令中的参数

        TASK_PATH = args.config
        #config_abs_path = os.path.abspath(TASK_PATH)#转化为绝对路径
        #config_dir = os.path.dirname(config_abs_path)#获取task.yaml所在的目录
        with open(TASK_PATH) as f:
            Task = yaml.safe_load(f)
            if Task is None:
                raise ValueError(f"错误：任务配置文件 '{TASK_PATH}' 为空。")
            
        timeout = Task["timeout"]
        task_list = Task.get("tasks", [])

    except KeyError as e:
        raise KeyError(f"错误：task.yaml文件中缺少键 {e}")
    except FileNotFoundError:
        raise FileNotFoundError(f"任务配置文件 '{TASK_PATH}' 路径错误或不存在。")
    return Task,timeout,task_list