import yaml
import csv
import math

#初始化函数：指定YAML文件路径，打开并转化为Python可读形式返回为cfg
def init_cfg():
    CONFIG_PATH = "config.yaml"
    with open(CONFIG_PATH) as f:
        cfg = yaml.safe_load(f)
    return cfg


#cfg读取函数：从cfg中读取并返回CSV文件路径和YAML配置文件中指定的列名
def read_cfg(cfg):
    csv_path = cfg["input_csv"]
    col_x = cfg["columns"]["x"]
    col_y = cfg["columns"]["y"]
    return csv_path, col_x, col_y


#数据读取函数：定义两个列表，打开数据文件并将每一行以字典格式读取为reader，键为表头，值为单元格，遍历reader将各值填入列表，返回两个列表
def read_data(csv_path, col_x, col_y):
    xs = []
    ys = []
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            xs.append(float(row[col_x]))
            ys.append(float(row[col_y]))
    return xs, ys

#求和函数：遍历列表各值求和
def sum_data(xs,ys):
    n = len(xs)
    sum_x = 0.0
    sum_y = 0.0
    for i in range(n):
        sum_x += xs[i]
        sum_y += ys[i]
    return n, sum_x, sum_y

#求平均值
def mean_data(n, sum_x, sum_y):
    mean_x = sum_x / n
    mean_y = sum_y / n
    return mean_x, mean_y


#按公式计算相关系数
def calcualtion(n,xs, ys, mean_x, mean_y):
    dx = 0.0
    dy = 0.0
    prod = 0.0
    for i in range(n):
        a = xs[i] - mean_x
        b = ys[i] - mean_y
        dx = dx + a * a
        dy = dy + b * b
        prod = prod + a * b
    denom = dx * dy
    r = prod / denom
    return r
cfg=init_cfg()
csv_path, col_x, col_y = read_cfg(cfg)
xs, ys = read_data(csv_path, col_x, col_y)
n, sum_x, sum_y = sum_data(xs, ys)
mean_x, mean_y = mean_data(n, sum_x, sum_y)
r = calcualtion(n, xs, ys, mean_x, mean_y)

print("n =", n)
print("mean_x =", mean_x)
print("mean_y =", mean_y)
print("r =", r)