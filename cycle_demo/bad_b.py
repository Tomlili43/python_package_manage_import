"""坏例子 B：同样在顶层 import 对方的名字。"""

from .bad_a import A_NAME  # 此刻 bad_a 才执行到第 3 行，A_NAME 还没定义

B_NAME = "b"


def b() -> str:
    return f"b + {A_NAME}"
