"""跨分支引用：orders → catalog.books（绝对导入）。

orders 和 catalog 是兄弟包，谁也不属于谁，所以这里写全路径最清楚。
"""

from shop import IMPORT_LOG
from shop.catalog.base import money
from shop.catalog.books.pricing import describe, price_with_tax

IMPORT_LOG.append("shop.orders.receipt")


def render_receipt(items: list) -> str:
    lines = [f"  {describe(item)}" for item in items]
    total = sum(price_with_tax(item) for item in items)
    lines.append(f"  合计 {money(total)}")
    return "\n".join(lines)
