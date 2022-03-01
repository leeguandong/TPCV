'''
@Time    : 2022/2/28 16:05
@Author  : leeguandon@gmail.com
'''
from enum import Enum


class Priority(Enum):
    """Hook priority levels.

    +--------------+------------+
    | Level        | Value      |
    +==============+============+
    | HIGHEST      | 0          |
    +--------------+------------+
    | VERY_HIGH    | 10         |
    +--------------+------------+
    | HIGH         | 30         |
    +--------------+------------+
    | ABOVE_NORMAL | 40         |
    +--------------+------------+
    | NORMAL       | 50         |
    +--------------+------------+
    | BELOW_NORMAL | 60         |
    +--------------+------------+
    | LOW          | 70         |
    +--------------+------------+
    | VERY_LOW     | 90         |
    +--------------+------------+
    | LOWEST       | 100        |
    +--------------+------------+
    """

    HIGHEST = 0
    VERY_HIGH = 10
    HIGH = 30
    ABOVE_NORMAL = 40
    NORMAL = 50
    BELOW_NORMAL = 60
    LOW = 70
    VERY_LOW = 90
    LOWEST = 100


def get_priority(priority):
    if isinstance(priority, str):
        return Priority[priority.upper()].value
