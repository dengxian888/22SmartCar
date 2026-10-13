from init_yaml import init_yaml
from build_graph import build_graph
from using_graph import using_graph

def main():
    Task, timeout,task_list= init_yaml()
    print("任务配置文件内容：")
    print("超时时间：", timeout)
    print("任务列表：", task_list)
    adj_list,in_degree=build_graph(task_list)
    using_graph(task_list,timeout,adj_list,in_degree)

if __name__ == "__main__":
    main()
