"""购物车：演示「跨分支的相对导入」和「函数内延迟导入」。"""

from shop import IMPORT_LOG
from ..catalog.books.models import Book  # 相对导入跨到兄弟包 catalog
from .receipt import render_receipt  # 相对导入同包内的兄弟模块

IMPORT_LOG.append("shop.orders.cart")


class Cart:
    def __init__(self) -> None:
        self.items: list[Book] = []

    def add(self, item: Book) -> None:
        self.items.append(item)

    def preview(self) -> str:
        """小票预览：orders 自己就能算账。"""
        return render_receipt(self.items)

    def checkout(self, email: str) -> str:
        """结账时才去拿通知渠道。

        为什么写在函数里，而不是文件顶部：emailer 反过来 import 了 orders.receipt，
        写在顶部的话，`import cart` 就会顺带把 notify 整条链（notify → channels →
        emailer → receipt）一起拉起来。放进函数，这条链等真要发邮件时才加载。

        注意：这么做**不是**为了避免报错——`from ...orders.receipt import ...` 引的是
        子模块，父包初始化一半时也能加载，不会报错。真正会炸的是从包的 __init__.py
        里取 re-export 出来的名字（见 cycle_demo/ 的对照实验）。
        """
        from ..notify.channels.emailer import Emailer

        receipt = render_receipt(self.items)
        Emailer().send(email, receipt)
        return receipt
