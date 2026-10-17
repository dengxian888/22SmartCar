from init_yaml import init_yaml
from build_graph import build_graph
from using_graph import using_graph
from write_json import write_json
from check_cycle import CycleError
import sys
import yaml
import random

def main():
    try:
        Task, timeout,task_list,report_path,seed= init_yaml()
        if seed is not None:
            random.seed(seed)
        adj_list,in_degree=build_graph(task_list)
        is_timeout,total_real_time,task_status=using_graph(task_list,timeout,adj_list,in_degree)
        write_json(is_timeout,total_real_time,task_status,report_path)
    except CycleError as e:
        print(f"错误：{e}")
        sys.exit(1)
        
    except FileNotFoundError as e:
        print(f"错误：{e}")
        sys.exit(1)

    except TypeError as e:
        print(f"错误:{e}")
        sys.exit(1)

    except KeyError as e:
        print(f"错误:{e}")
        sys.exit(1)

    except ValueError as e:
        print(f"错误:{e}")
        sys.exit(1)
        
    except Exception as e:
        print(f"错误：{e}")
        sys.exit(1)

    except yaml.YAMLError as e:
        print(f"错误：{e}")

if __name__ == "__main__":
    main()
