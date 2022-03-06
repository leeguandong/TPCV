'''
@Time    : 2022/2/28 16:58
@Author  : leeguandon@gmail.com
'''
import tpcv

from .hook import HOOKS, Hook


@HOOKS.register_module()
class OptimizerHook(Hook):
    def __init__(self, grad_clip=None, detect_anomalous_params=False):
        self.grad_clip = grad_clip
        self.detect_anomalous_params = detect_anomalous_params

    def after_train_iter(self, runner):
        """如果一个batch之后没有调用optimizer.zero_grad()，那么这个batch引入的梯度会暂存在参数
        w.grad中，下一个batch带来的grad会累加到w.grad里，这样相当于增大了batch_size,调用optimizer.zero_grad
        常规情况下，每个batch需要调用一次optimizer.zero_grad函数，把参数的梯度清零。
        """
        runner.optimizer.zero_grad()
        runner.outputs["loss"].backward()
        runner.optimizer.step()
