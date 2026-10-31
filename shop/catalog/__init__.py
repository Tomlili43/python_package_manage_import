"""第 2 层包：catalog —— `__init__.py` 当「门面」用。

对外只暴露 Book，调用方写 `from shop.catalog import Book` 就行，
不必知道 Book 其实藏在 catalog/books/ 里。以后挪位置，调用方不用改。
"""

from shop import IMPORT_LOG

IMPORT_LOG.append("shop.catalog")

from .books.models import Book

__all__ = ["Book"]
