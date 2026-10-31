"""catalog 的公共基类与金额工具。

它不 import 项目里任何模块，是依赖图的「叶子」——谁都可以引它，它不欠任何人。
"""


class Item:
    """所有商品的共同接口。"""

    def __init__(self, title: str, price: float) -> None:
        self.title = title
        self.price = price

    def label(self) -> str:
        return f"{self.title} {money(self.price)}"


def money(value: float) -> str:
    """统一金额格式，免得每个模块各写一遍。"""
    return f"¥{value:.2f}"
