import yaml
import argparse
import os
#初始化函数：给定YAML文件路径，打开并转化为Python可读形式返回为cfg
def init_cfg():
    try:
        parser = argparse.ArgumentParser(description="我的程序") #建立参数解析
        parser.add_argument("--config", type=str, default="config.yaml", help="配置文件路径")
        args = parser.parse_args()  #抓取命令中的参数

        CONFIG_PATH = args.config
        config_abs_path = os.path.abspath(CONFIG_PATH)#转化为绝对路径
        config_dir = os.path.dirname(config_abs_path)#获取config.yaml所在的目录
        with open(CONFIG_PATH) as f:
            cfg = yaml.safe_load(f)
            if cfg is None:
                raise ValueError(f"错误：配置文件 '{CONFIG_PATH}' 为空。")
    except FileNotFoundError:
        raise FileNotFoundError(f"配置文件 '{CONFIG_PATH}' 路径错误或不存在。")
    return cfg,config_dir