"""坏例子 A：在顶层 import 对方的名字。"""

from .bad_b import B_NAME  # 一进来就要 B_NAME，可 bad_b 又要回来拿 A_NAME

A_NAME = "a"


def a() -> str:
    return f"a + {B_NAME}"
