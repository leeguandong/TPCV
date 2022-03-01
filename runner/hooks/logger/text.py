'''
@Time    : 2022/2/28 17:59
@Author  : leeguandon@gmail.com
'''
import os.path as osp
from .base import LoggerHook
from ..hook import Hook, HOOKS


@HOOKS.register_module()
class TextLoggerHook(LoggerHook):
    def __init__(self,
                 by_epoch=True,
                 interval=10,
                 ignore_last=True,
                 reset_flag=False,
                 interval_exp_name=1000,
                 out_dir=None,
                 out_suffix=('.log.json', '.log', '.py'),
                 keep_local=True,
                 file_client_args=None):
        super(TextLoggerHook, self).__init__(interval, ignore_last, reset_flag,
                                             by_epoch)

        self.by_epoch = by_epoch
        self.time_sec_tot = 0
        self.interval_exp_name = interval_exp_name
        self.out_dir = out_dir
        self.keep_local = keep_local
        self.file_client_args = file_client_args

    def before_run(self, runner):
        super(TextLoggerHook, self).before_run(runner)

        self.start_iter = runner.iter
        self.json_log_path = osp.join(runner.work_dir, f"{runner.timestamp}.log.json")
