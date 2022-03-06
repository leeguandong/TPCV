'''
@Time    : 2022/3/2 15:09
@Author  : leeguandon@gmail.com
'''
import io
import tpcv
import time
import torch

from collections import OrderedDict
from torch.optim import Optimizer
from ..fileio import FileClient


def _save_to_state_dict(module, destination, prefix, keep_vars):
    for name, param in module._parameters.items():
        if param is not None:
            destination[prefix + name] = param if keep_vars else param.detach()
    for name, buf in module._buffers.items():
        if buf is not None:
            destination[prefix + name] = buf if keep_vars else buf.detach()


def get_state_dict(module, destination=None, prefix="", keep_vars=False):
    if destination is None:
        destination = OrderedDict()
        destination._metadata = OrderedDict()
    destination._metadata[prefix[:-1]] = local_metadata = dict(version=module._version)
    _save_to_state_dict(module, destination, prefix, keep_vars)
    for name, child in module._modules.items():
        if child is not None:
            get_state_dict(child, destination, prefix + name + ".", keep_vars=keep_vars)
    for hook in module._state_dict_hooks.values():
        hook_result = hook(module, destination, prefix, local_metadata)
        if hook_result is not None:
            destination = hook_result
    return destination


def weights_to_cpu(state_dict):
    state_dict_cpu = OrderedDict()
    for key, val in state_dict.items():
        state_dict_cpu[key] = val.cpu()
    state_dict_cpu._metadata = getattr(state_dict, "_metadata", OrderedDict())
    return state_dict_cpu


def save_checkpoint(model,
                    filename,
                    optimizer=None,
                    meta=None,
                    file_client_args=None):
    if meta is None:
        meta = {}

    meta.update(tpcv_version=tpcv.__version__, time=time.asctime())

    checkpoint = {
        "meta": meta,
        "state_dict": weights_to_cpu(get_state_dict(model))
    }

    if isinstance(optimizer, Optimizer):
        checkpoint["optimizer"] = optimizer.state_dict()

    file_client = FileClient.infer_client(file_client_args, filename)
    with io.BytesIO() as f:
        torch.save(checkpoint, f)
        file_client.put(f.getvalue(), filename)
