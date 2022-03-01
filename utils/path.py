'''
@Time    : 2022/2/28 11:55
@Author  : leeguandon@gmail.com
'''
import os
import os.path as osp


def mkdir_or_exist(dir_name, mode=0o777):
    if dir_name == "":
        return
    dir_name = osp.expanduser(dir_name)
    os.makedirs(dir_name, mode=mode, exist_ok=True)
