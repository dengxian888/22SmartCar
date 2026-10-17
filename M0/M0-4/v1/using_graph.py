from random_rate import rate
from check_cycle import check_cycle
from check_cycle import CycleError
import time
COLOR_GREEN = '\033[92m'  # 绿色
COLOR_RED = '\033[91m'    # 红色
COLOR_YELLOW = '\033[93m' # 黄色
COLOR_BLUE = '\033[94m'   # 蓝色
COLOR_RESET = '\033[0m'   # 重置颜色

def using_graph(task_list,timeout,adj_list,in_degree):
    try:
    # 把列表转换成字典
        task_dict = {task["name"]: task for task in task_list}
    except KeyError as e:
        raise KeyError (f"错误:缺少{e}键")
    ready_list = []
    #检查入度表，找出入度为0的任务
    for task in in_degree:
        if in_degree[task] == 0:
            ready_list.append(task)
    #检测是否有环依赖
    check_cycle(adj_list, in_degree)

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
                        "status": "TIMEOUT",
                        "attempt":"0",
                        "duration":"0",
                        "started_at":" ",
                        "ended_at":" "
                    }
            break
        try:
            current_task = ready_list.pop(0)
            success_rate=task_dict[current_task]["success_rate"]
            if success_rate >1:
                raise ValueError("根本没有这样的成功率......")
            
            duration=task_dict[current_task]["duration"]
        except KeyError as e:
            raise KeyError(f"键{e}不存在")

        total_duration+=duration

        #模拟任务执行
        try:
            task_start=time.time()
            time.sleep(duration)  # 模拟任务执行的时间
            task_duration=0
            task_duration+=duration
            current_rate = rate()
            n=1
            #如果任务执行失败，重试最多2次
            while current_rate > success_rate:
                print(f"{COLOR_RED}任务 {current_task} 执行失败!{COLOR_RESET}")
                is_success = False
                total_duration+=duration
                print(f"{COLOR_YELLOW}任务 {current_task} 正在重试第 {n} 次...{COLOR_RESET}")
                time.sleep(duration)
                task_duration+=duration
                n+=1
                if n==3:
                    print(f"任务 {current_task} 执行失败3次，跳过该任务。")
                    task_end=time.time()
                    break
                total_real_time = time.time() - start_time #当前执行时间
                if total_real_time > timeout:
                    is_timeout=True
                    task_end=time.time()
                    print(f"TIMEOUT,已执行时间：{total_real_time}秒")
                    for task in task_dict.keys():
                        task_status[current_task]={
                            "status":"TIMEOUT",
                            "attempt":n,
                            "duration":task_duration,
                            "started_at":task_start,
                            "ended_at":task_end

                        }
                        if task not in task_status:
                            task_status[task] = {
                                "status": "TIMEOUT",
                                "attempt":0,
                                "duration":0,
                                "started_at":" ",
                                "ended_at":" "
                            }
                    break#跳出当前循环
                current_rate= rate()


            if is_timeout:
                print(f"TIMEOUT,已执行时间：{total_real_time}秒")
                break#停止执行所有任务



            total_real_time = time.time() - start_time #当前执行时间
            if total_real_time > timeout:
                is_timeout=True
                task_end=time.time()
                print(f"TIMEOUT,已执行时间：{total_real_time}秒")
                for task in task_dict.keys():
                    task_status[current_task]={
                        "status":"TIMEOUT",
                        "attempt":n,
                        "duration":task_duration,
                        "started_at":task_start,
                        "ended_at":task_end

                    }
                    if task not in task_status:
                        task_status[task] = {
                            "status": "TIMEOUT",
                            "attempt":0,
                            "duration":0,
                            "started_at":" ",
                            "ended_at":" "
                        }
            if is_timeout:
                print(f"TIMEOUT,已执行时间：{total_real_time}秒")
                break#停止执行所有任务

            if current_rate <= success_rate:
                is_success = True
                task_end=time.time()

            if is_success:
                print(f"{COLOR_GREEN}任务 {current_task} 执行成功！{COLOR_RESET}")
                task_status[current_task] = {
                    "status": "SUCCESS",
                    "attempt":n,
                    "duration":task_duration,
                    "started_at":task_start,
                    "ended_at":task_end
                }
                # 更新下游任务的入度
                for child in adj_list[current_task]:
                    in_degree[child] -= 1
                    if in_degree[child] == 0:
                        ready_list.append(child)

            else:
                print(f"{COLOR_RED}任务 {current_task} 执行失败！{COLOR_RESET}")
                task_status[current_task] = {
                    "status": "FAILED",
                    "attempt":3,
                    "duration":task_duration,
                    "started_at":task_start,
                    "ended_at":task_end
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
                                "status": "SKIPPED",
                                "attempt":0,
                                "duration":0,
                                "started_at":" ",
                                "ended_at":" "
                            }
                            skip_queue.append(child)
        except TypeError as e:
            raise TypeError (f"{e}值类型错误")
    total_real_time=time.time()-start_time  #最后再进行一次任务计时
    return is_timeout,total_real_time,task_status

