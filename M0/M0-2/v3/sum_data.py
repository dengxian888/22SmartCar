#求和函数：遍历列表各值求和
def sum_data(xs,ys):
    n = len(xs)
    sum_x = 0.0
    sum_y = 0.0
    for i in range(n):
        sum_x += xs[i]
        sum_y += ys[i]
    return n, sum_x, sum_y