'''
@Time    : 2022/2/28 14:00
@Author  : leeguandon@gmail.com
'''
import inspect


def build_from_cfg(cfg, registry, default_args=None):
    """把config中的类转成框架中的类，是在dict中查找类的过程
    """
    args = cfg.copy()

    if default_args is not None:
        for name, value in default_args.items():
            args.setdefault(name, value)

    obj_type = args.pop("type")
    if isinstance(obj_type, str):
        obj_cls = registry.get(obj_type)

    return obj_cls(**args)


class Registry:
    """把框架中的类放到dict中
    """

    def __init__(self, name, build_func=None, parent=None, scope=None):
        self._name = name
        self._module_dict = dict()
        self._children = dict()

        self.build_func = build_from_cfg

    def __len__(self):
        return len(self._module_dict)

    @property
    def name(self):
        return self._name

    @property
    def module_dict(self):
        return self._module_dict

    def get(self, key):
        return self._module_dict[key]

    def _register_module(self, module_class, module_name=None, force=False):
        # if module_name is None:
        #     module_name = module_class.__name__
        # if isinstance(module_name, str):
        #     module_name = [module_name]
        # for name in module_name:
        #     if not force and name in self._module_dict:
        #         raise KeyError(f'{name} is already registered '
        #                        f'in {self.name}')
        #     self._module_dict[name] = module_class
        self._module_dict[module_class.__name__] = module_class

    def register_module(self, name=None, force=False, module=None):
        # 指定类 x.register_module(module=SomeClass)
        if module is not None:
            self._register_module(module_class=module, module_name=name, force=force)
            return module

        def _register(cls):
            self._register_module(
                module_class=cls, module_name=name, force=force)
            return cls

        return _register
