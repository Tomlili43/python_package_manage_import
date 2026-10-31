"""第 3 层，反向跨回 orders：3 个点。

    ...orders.receipt  →  shop.orders.receipt   （先爬到 shop，再下到另一根树枝）
    ..base             →  shop.notify.base
"""

from shop import IMPORT_LOG
from ...orders.receipt import render_receipt  # 3 个点：跨分支到兄弟树 orders
from ..base import Notifier  # 2 个点：回到 notify

IMPORT_LOG.append("shop.notify.channels.emailer")


class Emailer(Notifier):
    channel = "email"

    def send(self, to: str, body: str) -> None:
        print(f"  [email] → {to}")
        print(body)

    def send_receipt(self, to: str, items: list) -> None:
        """自己就能开票：这就是「反向依赖」的用武之地。"""
        self.send(to, render_receipt(items))
