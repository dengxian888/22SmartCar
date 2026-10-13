from random_rate import rate
import time

def using_graph(task_list,timeout,adj_list,in_degree):
    # 把列表转换成字典
    task_dict = {task["name"]: task for task in task_list}
    ready_list = []
    #检查入度表，找出入度为0的任务
    for task in in_degree:
        if in_degree[task] == 0:
            ready_list.append(task)
    if not ready_list:
        print("没有任务可以立即执行，可能存在循环依赖或所有任务都有依赖。")
    start_time = time.time()
    total_duration=0
    #按照拓扑排序的顺序执行任务

    while ready_list:
        total_real_time = time.time() - start_time
        if total_real_time > timeout:
            print(f"计时超时,已执行时间：{total_real_time}秒")
            break
        current_task = ready_list.pop(0)
        success_rate=task_dict[current_task]["success_rate"]
        duration=task_dict[current_task]["duration"]

        total_duration+=duration

        #模拟任务执行
        time.sleep(duration)  # 模拟任务执行的时间
        current_rate = rate()
        n=1
        #如果任务执行失败，重试最多2次
        while current_rate > success_rate:
            print(f"任务 {current_task} 执行失败，重试")
            total_duration+=duration
            time.sleep(duration)
            n+=1
            if n>3:
                print(f"任务 {current_task} 执行失败超过3次，跳过该任务。")
                break
            if total_real_time > timeout:
                print(f"计时超时,已执行时间：{total_real_time}秒")
                break
            current_rate= rate()


        for child in adj_list[current_task]:
            in_degree[child] -= 1
            if in_degree[child] == 0:
                ready_list.append(child)
