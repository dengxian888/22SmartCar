import csv
import sys
#数据读取函数：定义两个列表，打开数据文件并将每一行以字典格式读取为reader，键为表头，值为单元格，遍历reader将各值填入列表，返回两个列表
def read_data(csv_path, col_x, col_y):
    xs = []
    ys = []
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        #检查文件是否为空
        if reader.fieldnames is None:
            raise ValueError(f"数据文件 '{csv_path}' 完全为空，没有任何内容。")
        #检查列名是否匹配
        if col_x not in reader.fieldnames:
            raise KeyError(f"配置文件中的 x 列名 '{col_x}' 在 CSV 中不存在。CSV 实际表头为: {reader.fieldnames}")
        if col_y not in reader.fieldnames:
            raise KeyError(f"配置文件中的 y 列名 '{col_y}' 在 CSV 中不存在。CSV 实际表头为: {reader.fieldnames}")
        #检查每一列是否存在异常数据
        for row in reader:
            try:
                xs.append(float(row[col_x]))
                ys.append(float(row[col_y]))
            except ValueError:
                raise ValueError(f"在数据文件 '{csv_path}' 中，行 {reader.line_num} 的列 '{col_x}' 或 '{col_y}' 包含异常数据。")
        #检查是否存在空表头
        if len(xs) == 0 or len(ys) == 0:
            raise ValueError(f"数据文件 '{csv_path}' 中存在空表头。")
        if len(xs) != len(ys):
            raise ValueError(f"数据文件 '{csv_path}' 中列 '{col_x}' 和列 '{col_y}' 的数据长度不一致。") 
    return xs, ys