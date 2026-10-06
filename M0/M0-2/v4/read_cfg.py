import sys
#cfg读取函数：从cfg中读取键并返回CSV文件路径和数据文件的列名
def read_cfg(cfg):
    try:
        csv_path = cfg["input_csv"]
        col_x = cfg["columns"]["x"]
        col_y = cfg["columns"]["y"]
    except KeyError as e:
        raise KeyError(f"错误：cfg文件中缺少键 {e}")
    else:
        return csv_path, col_x, col_y