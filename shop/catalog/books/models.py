"""相对导入示例。

文件在 shop/catalog/books/ 下，那么：

    ..base   →  shop.catalog.base    「2 个点」回到上一层包 catalog
    ...      →  shop                 「3 个点」跨到最外层包

点的个数就是往树上爬几级，跟文件自己在第几层无关。
"""

from ... import IMPORT_LOG, __version__  # 3 个点：拿到顶层包的常量
from ..base import Item, money  # 2 个点：回到 catalog 拿基类

IMPORT_LOG.append("shop.catalog.books.models")


class Book(Item):
    """一本书也是一个 Item。"""

    kind = "book"

    def __init__(self, title: str, price: float, author: str = "匿名") -> None:
        super().__init__(title, price)
        self.author = author

    def label(self) -> str:
        return f"《{self.title}》 {self.author} {money(self.price)}"

    @property
    def from_version(self) -> str:
        """最深处也能取到顶层包的常量，就是靠 `from ... import`。"""
        return __version__
