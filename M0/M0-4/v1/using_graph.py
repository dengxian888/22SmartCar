from random_rate import rate
import time
COLOR_GREEN = '\033[92m'  # 绿色
COLOR_RED = '\033[91m'    # 红色
COLOR_YELLOW = '\033[93m' # 黄色
COLOR_BLUE = '\033[94m'   # 蓝色
COLOR_RESET = '\033[0m'   # 重置颜色

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
    is_timeout = False  # 默认不超时
    start_time = time.time()
    total_duration=0
    task_status={}

    #按照拓扑排序的顺序执行任务
    while ready_list:
        total_real_time = time.time() - start_time
        if total_real_time > timeout:
            is_timeout=True
            print(f"TIMEOUT,已执行时间：{total_real_time}秒")
            for task in task_dict.keys(): # 遍历所有任务
                if task not in task_status:
                    task_status[task] = {
                        "status": "FAILED"
                    }
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
            print(f"{COLOR_RED}任务 {current_task} 执行失败!{COLOR_RESET}")
            is_success = False
            total_duration+=duration
            print(f"{COLOR_YELLOW}任务 {current_task} 正在重试第 {n} 次...{COLOR_RESET}")
            time.sleep(duration)
            n+=1
            if n==3:
                print(f"任务 {current_task} 执行失败3次，跳过该任务。")
                break
            total_real_time = time.time() - start_time #当前执行时间
            if total_real_time > timeout:
                is_timeout=True
                print(f"TIMEOUT,已执行时间：{total_real_time}秒")
                for task in task_dict.keys():
                    if task not in task_status:
                        task_status[task] = {
                            "status": "FAILED"
                        }
                break#跳出当前循环
            current_rate= rate()

        if is_timeout:
            break#停止执行所有任务

        if current_rate <= success_rate:
            is_success = True

        if is_success:
            print(f"{COLOR_GREEN}任务 {current_task} 执行成功！{COLOR_RESET}")
            task_status[current_task] = {
                "status": "SUCCESS"
            }
            # 更新下游任务的入度
            for child in adj_list[current_task]:
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    ready_list.append(child)

        else:
            print(f"{COLOR_RED}任务 {current_task} 执行失败！{COLOR_RESET}")
            task_status[current_task] = {
                "status": "FAILED"
            }
            skip_queue = [current_task] #从当前失败的任务开始
            while skip_queue:
                failed_task = skip_queue.pop(0)
                
                # 遍历它的所有下游任务
                for child in adj_list[failed_task]:
                    # 如果下游任务还没执行
                    if child not in task_status:
                        print(f"{COLOR_BLUE}任务 {child}被跳过{COLOR_RESET}")
                        task_status[child] = {
                            "status": "SKIPPED"
                        }
                        skip_queue.append(child)
    total_real_time=time.time()-start_time
    return is_timeout,total_real_time,task_status

