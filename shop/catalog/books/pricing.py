"""绝对导入示例。

同一个包里的 models.py 用相对导入，这里故意全用绝对导入——
从最外层包写起，路径和「这个文件在第几层」完全无关，读起来永远是完整路径。
"""

from shop import IMPORT_LOG
from shop.catalog.base import money
from shop.catalog.books.models import Book

IMPORT_LOG.append("shop.catalog.books.pricing")

TAX_RATE = 0.06


def price_with_tax(book: Book) -> float:
    return round(book.price * (1 + TAX_RATE), 2)


def describe(book: Book) -> str:
    return f"{book.label()} → 含税 {money(price_with_tax(book))}"
