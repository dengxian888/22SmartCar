class CycleError(Exception):
    pass

def check_cycle(adj_list, in_degree):
    #在任务调度前，静态检测图中是否存在环依赖
    temp_in_degree = in_degree.copy()
    
    # 找出初始入度为 0 的任务
    temp_queue = [node for node in temp_in_degree if temp_in_degree[node] == 0]
    processed_count = 0

    
    while temp_queue:
        current = temp_queue.pop(0)
        processed_count += 1
        for child in adj_list[current]:
            temp_in_degree[child] -= 1
            if temp_in_degree[child] == 0:
                temp_queue.append(child)

    #如果剥离出的任务数<总任务数，说明有环
    if processed_count != len(in_degree):
        raise CycleError("检测到环依赖")