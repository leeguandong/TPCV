'''
@Time    : 2022/2/28 17:59
@Author  : leeguandon@gmail.com
'''

from abc import ABCMeta, abstractmethod

from ..hook import Hook, HOOKS


@HOOKS.register_module()
class LoggerHook(Hook):
    __metaclass__ = ABCMeta

    def __init__(self,
                 interval=10,
                 ignore_last=True,
                 reset_flag=False,
                 by_epoch=True):
        self.interval = interval
        self.ignore_last = ignore_last
        self.reset_flag = reset_flag
        self.by_epoch = by_epoch

    def before_run(self, runner):
        for hook in runner.hooks[::-1]:
            if isinstance(hook, LoggerHook):
                hook.reset_flag = True
                break

    def before_epoch(self, runner):
        runner.log_buffer.clear()
