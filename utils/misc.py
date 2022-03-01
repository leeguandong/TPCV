'''
@Time    : 2022/2/28 11:48
@Author  : leeguandon@gmail.com
'''

from collections import abc


def is_str(x):
    return isinstance(x, str)


def is_seq_of(seq, expected_type, seq_type=None):
    if seq_type is None:
        exp_seq_type = abc.Sequence
    else:
        assert isinstance(seq_type, type)
        exp_seq_type = seq_type
    if not isinstance(seq, exp_seq_type):
        return False
    for item in seq:
        if not isinstance(item, expected_type):
            return False
    return True


def is_list_of(seq, expected_type):
    return is_seq_of(seq, expected_type, seq_type=list)


def is_method_overridden(method, base_class, derived_class):
    """核心，从每个hook中找出它在这个节点是否有方法
    """
    if not isinstance(derived_class, type):
        derived_class = derived_class.__class__

    base_method = getattr(base_class, method)
    derived_method = getattr(derived_class, method)
    return derived_method != base_method
