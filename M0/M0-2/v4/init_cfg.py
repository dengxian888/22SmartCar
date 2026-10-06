import yaml
import sys
#初始化函数：指定YAML文件路径，打开并转化为Python可读形式返回为cfg
def init_cfg():
    try:
        CONFIG_PATH = "config.yaml"
        with open(CONFIG_PATH) as f:
            cfg = yaml.safe_load(f)
            if cfg is None:
                raise ValueError(f"错误：配置文件 '{CONFIG_PATH}' 为空。")
    except FileNotFoundError:
        raise FileNotFoundError(f"配置文件 '{CONFIG_PATH}' 路径错误或不存在。")
    return cfg