from init_yaml import init_yaml
from build_graph import build_graph
from using_graph import using_graph
from write_json import write_json

def main():
    Task, timeout,task_list= init_yaml()
    adj_list,in_degree=build_graph(task_list)
    is_timeout,total_real_time,task_status=using_graph(task_list,timeout,adj_list,in_degree)
    write_json(is_timeout,total_real_time,task_status)

if __name__ == "__main__":
    main()
