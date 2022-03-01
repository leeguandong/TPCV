'''
@Time    : 2022/2/28 13:57
@Author  : leeguandon@gmail.com
'''
import time
from .base_runner import BaseRunner
from .builder import RUNNERS


@RUNNERS.register_module()
class EpochBasedRunner(BaseRunner):
    def run_iter(self, data_batch, train_mode, **kwargs):
        if train_mode:
            outputs = self.model.train_step(data_batch, self.optimizer, **kwargs)
        else:
            outputs = self.model.val_step(data_batch, self.optimizer, **kwargs)
        self.outputs = outputs

    def train(self, data_loader, **kwargs):
        self.model.train()
        self.mode = "train"
        self.data_loader = data_loader
        self._max_iters = self._max_epochs * len(self.data_loader)

        self.call_hook("before_train_epoch")
        for i, data_batch in enumerate(self.data_loader):
            self._inner_iter = i
            self.call_hook("before_train_iter")
            self.run_iter(data_batch, train_mode=True, **kwargs)
            self.call_hook("after_train_iter")
            self._iter += 1

        self.call_hook("after_train_epoch")
        self._epoch += 1

    def run(self, data_loaders, workflow, max_epochs=None, **kwargs):
        assert isinstance(data_loaders, list)
        assert len(data_loaders) == len(workflow)

        for i, flow in enumerate(workflow):
            mode, epochs = flow
            if mode == "train":
                self._max_iters = self._max_epochs * len(data_loaders[i])
                break

        self.logger.info("workflow: %s, max: %d epochs", workflow, self._max_epochs)
        self.call_hook("before_run")

        while self.epoch < self._max_epochs:
            for i, flow in enumerate(workflow):
                mode, epochs = flow
                epoch_runner = getattr(self, mode)
                for _ in range(epochs):
                    if mode == "train" and self.epoch >= self._max_epochs:
                        break
                    epoch_runner(data_loaders[i], **kwargs)
        time.sleep(1)
        self.call_hook("after_run")

    def call_hook(self, fn_name):
        for hook in self._hooks:
            getattr(hook, fn_name)(self)
