import yaml
import csv
import math
import sys
from init_cfg import init_cfg
from read_data import read_data
from sum_data import sum_data
from mean_data import mean_data
from calculation import calculation
import unittest

class TestCorrelation(unittest.TestCase):

    #测试正常用例
    def test_1(self):
        """测试完全正相关，期望结果为 1.0"""
        xs = [1, 2, 3]
        ys = [2, 4, 6]
        n,sum_x, sum_y = sum_data(xs, ys)
        mean_x, mean_y = mean_data(n, sum_x, sum_y)
        result = calculation(n, xs, ys, mean_x, mean_y)
        self.assertAlmostEqual(result, 1.0, places=6)

    def test_2(self):
        """测试完全负相关，期望结果为-1.0"""
        xs = [1, 2, 3]
        ys = [6, 4, 2]
        n,sum_x, sum_y = sum_data(xs, ys)
        mean_x, mean_y = mean_data(n, sum_x, sum_y)
        result = calculation(n, xs, ys, mean_x, mean_y)
        self.assertAlmostEqual(result, -1.0, places=6)

    #测试异常用例
    def test_3(self):
        """测试零方差（一列数据完全一样），期望抛出 ValueError"""
        xs = [1, 1, 1]
        ys = [2, 3, 4]
        n,sum_x, sum_y = sum_data(xs, ys)
        mean_x, mean_y = mean_data(n, sum_x, sum_y)
        with self.assertRaises(ValueError):
            calculation(n, xs, ys, mean_x, mean_y)

    def test_4(self):
        """测试列名不匹配，期望抛出 KeyError"""
        with self.assertRaises(KeyError):
            read_data("test_data.csv", "sensor_a", "sensor_c")

    def test_5(self):
        """测试数据数量不匹配，期望抛出 ValueError"""
        with self.assertRaises(ValueError):
            read_data("test_data.csv", "sensor_a", "sensor_b")

if __name__ == '__main__':
    unittest.main()