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

    def before_iter(self, runner):
        runner.log_buffer.update({"data_time": time.time() - self.t})

    def after_iter(self, runner):
        runner.log_buffer.update({"time": time.time() - self.t})
        self.t = time.time()
