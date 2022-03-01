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
