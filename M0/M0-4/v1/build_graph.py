def build_graph(tasks_data):
    adj_list = {}
    in_degree = {}

    #初始化邻接表和入度表
    for task in tasks_data:
        name = task["name"]
        adj_list[name] = []
        in_degree[name] = 0

    #构建依赖
    for task in tasks_data:
        name = task["name"]
        for dep in task["dependencies"]:
            adj_list[dep].append(name)
            in_degree[name] += 1

    return adj_list, in_degree