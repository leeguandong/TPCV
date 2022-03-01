'''
@Time    : 2022/2/28 11:43
@Author  : leeguandon@gmail.com
'''
import warnings


class A():
    def __init__(self):
        self.val()
        self.step()

    def step(self):
        print("aaa")

    @staticmethod
    def val():
        print("222")

    def deprecated_register(self):
        warnings.warn("deprecated", DeprecationWarning)
        self.deprecated_register()
        return


# print(hasattr(A, "step"))
# A().deprecated_register()

for i in range(len([1, 2, 3, 4, 5]) - 1, -1, -1):
    print(i)
