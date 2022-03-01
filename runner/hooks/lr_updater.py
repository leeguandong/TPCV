'''
@Time    : 2022/2/28 15:20
@Author  : leeguandon@gmail.com
'''
import tpcv
from .hook import HOOKS, Hook


class LrUpdaterHook(Hook):
    def __init__(self,
                 by_epoch=True,
                 warmup=None,
                 warmup_iters=0,
                 warmup_ratio=0.1,
                 warmup_by_epoch=False):
        self.by_epoch = by_epoch
        self.warmup = warmup
        self.warmup_iters = warmup_iters
        self.warmup_ratio = warmup_ratio
        self.warmup_by_epoch = warmup_by_epoch

        self.base_lr = []
        self.regular_lr = []

    def _set_lr(self, runner, lr_groups):
        for param_group, lr in zip(runner.optimizer.param_groups, lr_groups):
            param_group["lr"] = lr

    def get_lr(self, runner, base_lr):
        raise NotImplementedError

    def get_regular_lr(self, runner):
        return [self.get_lr(runner, _base_lr) for _base_lr in self.base_lr]

    def before_run(self, runner):
        # resuming场景，后续就没有实现了
        if isinstance(runner.optimizer, dict):
            pass
        else:
            for group in runner.optimizer.param_groups:
                group.setdefault("initial_lr", group["lr"])
            self.base_lr = [group["initial_lr"] for group in runner.optimizer.param_groups]

    def before_train_epoch(self, runner):
        self.regular_lr = self.get_regular_lr(runner)
        self._set_lr(runner, self.regular_lr)


    def before_train_iter(self, runner):
        pass




@HOOKS.register_module()
class StepLrUpdateHook(LrUpdaterHook):
    def __init__(self, step, gamma=0.1, min_lr=None, **kwargs):
        if isinstance(step, list):
            assert tpcv.is_list_of(step, int)
            assert all([s > 0 for s in step])

        self.step = step
        self.gamma = gamma
        self.min_lr = min_lr
        super(StepLrUpdateHook, self).__init__(**kwargs)

    def get_lr(self, runner, base_lr):
        """ step 中值表示 epoch
        """
        progress = runner.epoch if self.by_epoch else runner.iter

        exp = len(self.step)
        for i, s in enumerate(self.step):
            if progress < s:
                exp = i
                break

        lr = base_lr * (self.gamma ** exp)
        if self.min_lr is not None:
            lr = max(lr, self.min_lr)
        return lr
