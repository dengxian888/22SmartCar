#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sensor_analyzer.py  —— 上一届学长留下的"能用"的脚本

注释（学长原话）：
    "处理一下传感器数据就能用"

原本意图：
    1. 读取 sensor_data.csv（列：time, value）
    2. 计算 value 的平均值、标准差
    3. 剔除离群值（|value - mean| > 2 * std）
    4. 把清洗后的数据保存为 cleaned_data.csv
    5. 打印一份统计摘要

现状：跑不通 / 跑出来数不对。就交给你了。
"""

import csv
import os
import sys
from itertools import compress

INPUT_FILE = "sensor_data.csv"
OUTPUT_FILE = "cleaned_data.csv"
OUTPUT_DIR = "out"  # 输出目录

print("=== 传感器数据分析 ===")

# --- 读取数据 ---
def read_data():
    try:
        data = []
        time = []
        reader = csv.DictReader(open(INPUT_FILE, "r"))
        if reader is None:
            raise ValueError(f"错误：输入文件 {INPUT_FILE} 为空")
        line_num=1
        for row in reader:
            if not row.get("value") or not row.get("time"):
                raise ValueError(f"错误：数据缺失，{line_num}行缺少 time 或 value 列，当前行内容: {row}")
            t = float(row["time"])
            v = float(row["value"])

            time.append(t)
            data.append(v)
            line_num+=1
            if len(data)==0:
                raise ValueError(f"错误：输入文件 {INPUT_FILE} 中没有数据")
        print("共读取 %d 条数据" % len(data))
    except FileNotFoundError as e:
        raise FileNotFoundError(f"错误：未找到输入文件 {INPUT_FILE}")
    except TypeError as e:
        raise TypeError(f"错误:输入文件 {INPUT_FILE}中有数据类型不正确")
    return time, data

# --- 计算平均值 ---
def mean_calculation(data):
    total = 0
    for v in data:
        total += v
    mean = total / len(data)
    return mean

# --- 计算标准差 ---
def std_calculation(data, mean):
    acc = 0
    for v in data:
        acc += (v - mean) ** 2
    std = (acc / len(data)) ** 0.5
    return std

# --- 剔除离群值 ---
def remove_data(times, data, mean, std):
    #生成布尔列表选择器，符合为True
    selectors = [abs(v - mean) <= 2 * std for v in data]
    #将迭代器转化为列表
    times = list(compress(times, selectors))
    data = list(compress(data, selectors))
    cleaned_data = data
    cleaned_times = times
    return cleaned_times, cleaned_data


# --- 输出清洗后的数据 ---
def output(cleaned_times,cleaned_data):
    try:
        #输出路径
        output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
        #生成out目录
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        f = open(output_path, "w")
        writer = csv.writer(f)
        writer.writerow(["times", "value"])
        for t,v in zip(cleaned_times,cleaned_data):
            writer.writerow([f"{t:.2f}",v])
    except FileNotFoundError as e:
        raise FileNotFoundError(f"错误：输出文件所在目录{OUTPUT_DIR}创建失败失败")
    return output_path

def main():
    try:  
        time, data = read_data()
        mean = mean_calculation(data)
        std= std_calculation(data, mean)
        cleaned_time, cleaned_data = remove_data(time, data, mean, std)
        output_path = output(cleaned_time, cleaned_data)

        print("均值 mean = %.4f" % mean)
        print("标准差 std = %.4f" % std)
        print("清洗后剩余 %d 条" % len(cleaned_data))
        print("已保存到 %s" % output_path)
    except Exception as e:
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    main()
