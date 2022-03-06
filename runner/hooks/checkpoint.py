'''
@Time    : 2022/2/28 17:20
@Author  : leeguandon@gmail.com
'''
import tpcv
from .hook import HOOKS, Hook
from tpcv.fileio import FileClient


@HOOKS.register_module()
class CheckpointHook(Hook):
    def __init__(self,
                 interval=-1,
                 by_epoch=True,
                 save_optimizer=True,
                 out_dir=None,
                 max_keep_ckpts=-1,
                 save_last=True,
                 sync_buffer=False,
                 file_client_args=None,
                 **kwargs):
        self.interval = interval
        self.by_epoch = by_epoch
        self.save_optimizer = save_optimizer
        self.out_dir = out_dir
        self.max_keep_ckpts = max_keep_ckpts
        self.save_last = save_last
        self.args = kwargs
        self.sync_buffer = sync_buffer
        self.file_client_args = file_client_args

    def before_run(self, runner):
        """ 主要是取到存储数据的file_client
        """
        if not self.out_dir:
            self.out_dir = runner.work_dir

        self.file_client = FileClient.infer_client(self.file_client_args, self.out_dir)

        runner.logger.info((f'Checkpoints will be saved to {self.out_dir} by '
                            f'{self.file_client.name}.'))

        self.args['create_symlink'] = self.file_client.allow_symlink

    def after_train_iter(self, runner):
        if self.by_epoch:
            return

    def after_train_epoch(self, runner):
        if not self.by_epoch:
            return

        if self.every_n_epochs(runner, self.interval) or (self.save_last and self.is_last_epoch(runner)):
            runner.logger.info(f'Saving checkpoint at {runner.epoch + 1} epochs')
            self._save_checkpoint(runner)

    def _save_checkpoint(self, runner):
        runner.save_checkpoint(self.out_dir, save_optimizer=self.save_optimizer, **self.args)
