'''
@Time    : 2022/2/28 11:33
@Author  : leeguandon@gmail.com
'''
import os.path as osp
from abc import ABCMeta, abstractmethod

import tpcv
from .hooks import HOOKS, Hook

from .log_buffer import LogBuffer
from .priority import Priority, get_priority
from .utils import get_time_str


class BaseRunner(metaclass=ABCMeta):
    """
    raise error基本都是原生py中的exception
    """

    def __init__(self,
                 model,
                 optimizer=None,
                 work_dir=None,
                 logger=None,
                 meta=None,
                 max_iters=None,
                 max_epochs=None):
        assert hasattr(model, "train_step")

        self.model = model
        self.optimizer = optimizer
        self.logger = logger
        self.meta = meta

        if tpcv.is_str(work_dir):
            self.work_dir = osp.abspath(work_dir)

        if hasattr(self.model, "module"):
            self._model_name = self.model.module.__class__.__name__
        else:
            self._model_name = self.model.__class__.__name__

        self.timestamp = get_time_str()
        self.mode = None
        self._hooks = []
        self._epoch = 0
        self._iter = 0
        self._inner_iter = 0

        self._max_epochs = max_epochs
        self._max_iters = max_iters
        self.log_buffer = LogBuffer()

    @property
    def epoch(self):
        return self._epoch

    @property
    def hooks(self):
        return self._hooks

    def get_hook_info(self):
        stage_hook_map = {stage: [] for stage in Hook.stages}
        for hook in self.hooks:
            try:
                priority = Priority(hook.priority).name
            except ValueError:
                priority = hook.priority
            classname = hook.__class__.__name__
            hook_info = f"({priority}){classname}"
            for trigger_stage in hook.get_triggered_stage():
                stage_hook_map[trigger_stage].append(hook_info)

        stage_hook_infos = []
        for stage in Hook.stages:
            hook_infos = stage_hook_map[stage]
            if len(hook_infos) > 0:
                info = f'{stage}:\n'
                info += '\n'.join(hook_infos)
                info += '\n -------------------- '
                stage_hook_infos.append(info)
        return '\n'.join(stage_hook_infos)

    def register_hook(self, hook, priority="NORMAL"):
        assert isinstance(hook, Hook)
        priority = get_priority(priority)
        hook.priority = priority
        # hook list中添加 steplrupdaterhook
        inserted = False
        for i in range(len(self._hooks) - 1, -1, -1):
            if priority >= self._hooks[i].priority:
                self._hooks.insert(i + 1, hook)
                inserted = True
                break
        if not inserted:
            self._hooks.insert(0, hook)

    def register_lr_hook(self, lr_config):
        if lr_config is None:
            return
        if isinstance(lr_config, dict):
            assert "policy" in lr_config
            policy_type = lr_config.pop("policy")
            if policy_type == policy_type.lower():
                policy_type = policy_type.title()
            hook_type = policy_type + "LrUpdateHook"
            lr_config["type"] = hook_type
            hook = tpcv.build_from_cfg(lr_config, HOOKS)
        else:
            hook = lr_config
        self.register_hook(hook, priority="VERY_HIGH")

    def register_momentum_hook(self, momentum_config):
        if momentum_config is None:
            return

    def register_optimizer_hook(self, optimizer_config):
        if optimizer_config is None:
            return
        if isinstance(optimizer_config, dict):
            optimizer_config.setdefault("type", "OptimizerHook")
            hook = tpcv.build_from_cfg(optimizer_config, HOOKS)
        else:
            hook = optimizer_config
        self.register_hook(hook, priority="ABOVE_NORMAL")

    def register_checkpoint_hook(self, checkpoint_config):
        if checkpoint_config is None:
            return
        if isinstance(checkpoint_config, dict):
            checkpoint_config.setdefault("type", "CheckpointHook")
            hook = tpcv.build_from_cfg(checkpoint_config, HOOKS)
        else:
            hook = checkpoint_config
        self.register_hook(hook, priority="NORMAL")

    def register_timer_hook(self, timer_config):
        if timer_config is None:
            return
        if isinstance(timer_config, dict):
            hook = tpcv.build_from_cfg(timer_config, HOOKS)
        else:
            hook = timer_config
        self.register_hook(hook, priority="LOW")

    def register_logger_hooks(self, log_config):
        if log_config is None:
            return
        log_interval = log_config["interval"]
        for info in log_config["hooks"]:
            logger_hook = tpcv.build_from_cfg(info, HOOKS, default_args=dict(interval=log_interval))
            self.register_hook(logger_hook, priority="VERY_LOW")

    def register_custom_hooks(self, custom_config):
        if custom_config is None:
            return

    def register_training_hooks(self,
                                lr_config,
                                optimizer_config=None,
                                checkpoint_config=None,
                                log_config=None,
                                momentum_config=None,
                                timer_config=dict(type="IterTimeHook"),
                                custom_hooks_config=None):
        self.register_lr_hook(lr_config)
        self.register_momentum_hook(momentum_config)
        self.register_optimizer_hook(optimizer_config)
        self.register_checkpoint_hook(checkpoint_config)
        self.register_timer_hook(timer_config)
        self.register_logger_hooks(log_config)
        self.register_custom_hooks(custom_hooks_config)
