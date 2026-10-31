"""好例子 A：把 import 挪进函数，等调用时再拿。"""

A2_NAME = "a2"


def a2() -> str:
    from .good_b import b2  # 用到才导入，此刻 good_b 早已加载完毕

    return f"a2 + {b2()}"
