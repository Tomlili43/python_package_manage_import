"""可复用的演示流程：main.py 和 `python -m shop` 都调它。"""

from shop import IMPORT_LOG
from shop.catalog import Book  # 门面导入：不用知道 Book 藏在 catalog/books/
from shop.orders.cart import Cart
from shop.notify.channels.sms import Sms

IMPORT_LOG.append("shop.run")


def demo() -> None:
    cart = Cart()
    cart.add(Book("Python 包与导入", 68.0, "Ada"))
    cart.add(Book("流程控制", 42.5, "Linus"))

    print("\n--- 小票预览：orders → catalog.books.pricing")
    print(cart.preview())

    print("\n--- 结账：cart 在 checkout() 里延迟导入 notify.channels.emailer")
    cart.checkout("reader@example.com")

    print("\n--- 换个渠道发同一份小票：notify.channels.sms")
    Sms().send("13800000000", cart.preview())
