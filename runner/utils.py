'''
@Time    : 2022/2/28 13:44
@Author  : leeguandon@gmail.com
'''
import time


def get_time_str():
    return time.strftime("%Y%m%d_%H%M&S", time.localtime())
