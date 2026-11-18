import argparse
import sys
from task_fsm.core import TaskEngine
from task_fsm.logger import Logger

def main():
    parser = argparse.ArgumentParser(description="M5-1 纯软件状态机调度引擎")
    parser.add_argument("yaml_path", type=str, help="任务编排 YAML 文件路径")
    args = parser.parse_args()

    Logger.info(f"加载配置文件: {args.yaml_path}")
    try:
        engine = TaskEngine(args.yaml_path)
        status = engine.run()
        Logger.info(f"最终状态: {status}")
        sys.exit(0 if status == "SUCCESS" else 1)
    except Exception as e:
        Logger.error(f"执行异常: {e}")
        sys.exit(2)

if __name__ == "__main__":
    main()