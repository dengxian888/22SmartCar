import unittest
import yaml
import csv
import math
import sys
from init_cfg import init_cfg
from read_cfg import read_cfg
from read_data import read_data
from sum_data import sum_data
from mean_data import mean_data
from calculation import calculation

class TestCorrelation(unittest.TestCase):

    # --- 1. 测试正常用例 ---
    def test_perfect_positive(self):
        """测试完全正相关，期望结果为 1.0"""
        xs = [1, 2, 3]
        ys = [2, 4, 6]
        result = calculate_r(xs, ys)
        # 浮点数比较不能用 ==，要用 assertAlmostEqual 指定小数位数
        self.assertAlmostEqual(result, 1.0, places=4)

    def test_perfect_negative(self):
        """测试完全负相关，期望结果为 -1.0"""
        xs = [1, 2, 3]
        ys = [6, 4, 2]
        result = calculate_r(xs, ys)
        self.assertAlmostEqual(result, -1.0, places=4)

    # --- 2. 测试异常用例（任务要求的重点） ---
    def test_zero_variance(self):
        """测试零方差（一列数据完全一样），期望抛出 ValueError"""
        xs = [1, 1, 1]
        ys = [2, 3, 4]
        # 用 assertRaises 断言一定会抛出指定的异常
        with self.assertRaises(ValueError):
            calculate_r(xs, ys)

    def test_empty_data(self):
        """测试空数据，期望抛出 ValueError"""
        xs = []
        ys = []
        with self.assertRaises(ValueError):
            calculate_r(xs, ys)

    # --- 3. 测试文件读取（如缺列、空文件） ---
    # 这里需要你在本地临时建两个测试用的 csv 文件来模拟
    def test_missing_column(self):
        """测试列名不匹配，期望抛出 KeyError"""
        # 假设你本地有测试用的 'test_data.csv'，表头是 'a,b'
        # 这里传入错误的列名 'c'，应该触发 KeyError
        with self.assertRaises(KeyError):
            read_data("test_data.csv", "c", "b") 

# 固定写法，让 unittest 自动运行所有 test_ 开头的方法
if __name__ == '__main__':
    unittest.main()