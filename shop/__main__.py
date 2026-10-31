"""让 `python -m shop` 也能跑起来（相对导入写法）。"""

from .run import demo

if __name__ == "__main__":
    demo()
