class Logger:
    # 保留原有的基础方法
    @staticmethod
    def info(msg: str): print(f"\033[94m[INFO]      {msg}\033[0m")     # 蓝色
    @staticmethod
    def success(msg: str): print(f"\033[92m[SUCCESS]   {msg}\033[0m")  # 绿色
    @staticmethod
    def warn(msg: str): print(f"\033[93m[WARN]      {msg}\033[0m")     # 黄色
    @staticmethod
    def error(msg: str): print(f"\033[91m[ERROR]     {msg}\033[0m")    # 红色

    # 题目要求的五种专属颜色
    @staticmethod
    def transition(msg: str): print(f"\033[96m[TRANSITION] {msg}\033[0m") # 青色 - 状态转移
    @staticmethod
    def context(msg: str):    print(f"\033[95m[CONTEXT]    {msg}\033[0m") # 紫色 - 上下文变更
    @staticmethod
    def retry(msg: str):      print(f"\033[93m[RETRY]      {msg}\033[0m") # 黄色 - 重试
    @staticmethod
    def fallback(msg: str):   print(f"\033[91m[FALLBACK]   {msg}\033[0m") # 红色 - 降级
    @staticmethod
    def timeout(msg: str):    print(f"\033[97m[TIMEOUT]    {msg}\033[0m") # 亮白 - 超时