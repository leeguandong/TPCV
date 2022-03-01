'''
@Time    : 2022/2/28 17:33
@Author  : leeguandon@gmail.com
'''
import time
from .hook import HOOKS, Hook


@HOOKS.register_module()
class IterTimeHook(Hook):
    def before_epoch(self, runner):
        self.t = time.time()

