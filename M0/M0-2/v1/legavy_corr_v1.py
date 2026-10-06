import yaml
import csv
import math

CONFIG_PATH = "config.yaml"

#读取YAML配置文件并转化为python格式可读

with open(CONFIG_PATH) as f:
    cfg = yaml.safe_load(f)

#从YAML文件中读取数据存放路径并按配置规则读取两列数据

csv_path = cfg["input_csv"]
col_x = cfg["columns"]["x"]
col_y = cfg["columns"]["y"]

#定义两个列表

xs = []
ys = []

#打开数据文件并将每一行以字典格式读取为reader，键为表头，值为单元格，遍历reader将各值填入列表

with open(csv_path) as f:
    reader = csv.DictReader(f)
    for row in reader:
        xs.append(float(row[col_x]))
        ys.append(float(row[col_y]))

#遍历列表各值求和

n = len(xs)

sum_x = 0.0
sum_y = 0.0
for i in range(n):
    sum_x = sum_x + xs[i]
    sum_y = sum_y + ys[i]

#求平均值

mean_x = sum_x / n
mean_y = sum_y / n

#按公式计算相关系数

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

#打印数据

print("n =", n)
print("mean_x =", mean_x)
print("mean_y =", mean_y)
print("r =", r)
