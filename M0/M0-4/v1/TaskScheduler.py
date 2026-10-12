import init_yaml

def main():
    Task, timeout,task_list= init_yaml.init_cfg()
    print("任务配置文件内容：")
    print("超时时间：", timeout)
    print("任务列表：", task_list)

if __name__ == "__main__":
    main()
