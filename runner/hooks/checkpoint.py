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

