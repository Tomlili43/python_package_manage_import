"""好例子 B：同样延迟导入。"""

B2_NAME = "b2"


def b2() -> str:
    from .good_a import A2_NAME  # 只取值，不再触发 good_a 的模块体

    return f"b2 + {A2_NAME}"
