'''
@Time    : 2022/2/28 13:47
@Author  : leeguandon@gmail.com
'''
from collections import OrderedDict


class LogBuffer:
    def __init__(self):
        self.val_history = OrderedDict()
        self.n_history = OrderedDict()
        self.output = OrderedDict()
        self.ready = False
