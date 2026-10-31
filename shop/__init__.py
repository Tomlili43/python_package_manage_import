"""第 1 层包：shop。

这里只放版本号和一个「导入记录器」，刻意不 import 任何子包——
所以 `import shop` 很轻，子包什么时候被拉起来完全由调用方决定。
"""

__version__ = "1.0"

IMPORT_LOG: list[str] = []
IMPORT_LOG.append("shop")
