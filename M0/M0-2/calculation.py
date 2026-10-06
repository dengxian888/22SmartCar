#按公式计算相关系数
def calculation(n,xs, ys, mean_x, mean_y):
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
    if denom == 0:
        raise ValueError("计算相关系数时分母为零，可能是数据中存在异常值或所有 x 或 y 值相同。")
    r = prod / (denom**0.5)
    return r