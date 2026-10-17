def build_graph(tasks_data):
    adj_list = {}
    in_degree = {}

    try:
        #初始化邻接表和入度表
        for task in tasks_data:
            name = task["name"]
            adj_list[name] = []
            in_degree[name] = 0

        #构建依赖
        for task in tasks_data:
            name = task["name"]
            for dep in task["dependencies"]:
                if dep not in adj_list:
                    raise KeyError(f"任务{name}依赖了不存在的任务{dep}，请检查YAML配置")
                adj_list[dep].append(name)
                in_degree[name] += 1

    except KeyError as e:
        raise KeyError (f"{e}键不存在")

    return adj_list, in_degree