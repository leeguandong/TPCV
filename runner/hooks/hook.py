'''
@Time    : 2022/2/28 15:12
@Author  : leeguandon@gmail.com
'''
from tpcv.utils import Registry, is_method_overridden

HOOKS = Registry("hook")


class Hook:
    stages = ("before_run", "before_train_epoch", "before_train_iter", "after_train_iter",
              "after_train_epoch", "before_val_epoch", "before_val_iter", "after_val_iter",
              "after_val_epoch", "after_run")

    def before_run(self, runner):
        pass

    def after_run(self, runner):
        pass

    def before_epoch(self, runner):
        pass

    def after_epoch(self, runner):
        pass

    def before_iter(self, runner):
        pass

    def after_iter(self, runner):
        pass

    def before_train_epoch(self, runner):
        self.before_epoch(runner)

    def before_val_epoch(self, runner):
        self.before_epoch(runner)

    def after_train_epoch(self, runner):
        self.after_epoch(runner)

    def after_val_epoch(self, runner):
        self.after_epoch(runner)

    def before_train_iter(self, runner):
        self.before_iter(runner)

    def before_val_iter(self, runner):
        self.before_iter(runner)

    def after_train_iter(self, runner):
        self.after_iter(runner)

    def after_val_iter(self, runner):
        self.after_iter(runner)

    def get_triggered_stage(self):
        trigger_stages = set()
        for stage in Hook.stages:
            # stage 是点位，Hook 是基类，self 是传入的hook类,此处在取self类中对应基类的方法，这份方法是
            # 在不同的点位起作用的
            if is_method_overridden(stage, Hook, self):
                trigger_stages.add(stage)

        # 有的hook在before_epoch下的两个场景都用，因此会做简写
        method_stages_map = {
            'before_epoch': ['before_train_epoch', 'before_val_epoch'],
            'after_epoch': ['after_train_epoch', 'after_val_epoch'],
            'before_iter': ['before_train_iter', 'before_val_iter'],
            'after_iter': ['after_train_iter', 'after_val_iter'],
        }

        for method, map_stages in method_stages_map.items():
            if is_method_overridden(method, Hook, self):
                trigger_stages.update(map_stages)

        return [stage for stage in Hook.stages if stage in trigger_stages]
