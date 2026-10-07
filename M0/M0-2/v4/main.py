import sys
from init_cfg import init_cfg
from read_cfg import read_cfg
from read_data import read_data
from sum_data import sum_data
from mean_data import mean_data
from calculation import calculation



try:
    cfg,config_dir=init_cfg()
    csv_path, col_x, col_y,task,task_name= read_cfg(cfg)
    xs, ys = read_data(config_dir, csv_path, col_x, col_y)
    n, sum_x, sum_y = sum_data(xs, ys)
    mean_x, mean_y = mean_data(n, sum_x, sum_y)
    r = calculation(n, xs, ys, mean_x, mean_y)

    print("task_name=",task_name)
    if task is True:
        print("n =", n)
        print("mean_x =", mean_x)
        print("mean_y =", mean_y)
    print("r =", r)

except FileNotFoundError as e:
    print(f"错误：{e.filename}路径错误或不存在")
    sys.exit(1)
except KeyError as e: 
    print(f"错误：{e}")
    sys.exit(1)
except ValueError as e:
    print(f"错误：{e}")
    sys.exit(1)
