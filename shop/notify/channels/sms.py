"""第 3 层的另一个渠道：同层兄弟模块互不干扰。

它只认 notify.base，没被任何模块顶层引用——需要它的人自己导入即可。
"""

from shop import IMPORT_LOG
from ..base import Notifier

IMPORT_LOG.append("shop.notify.channels.sms")


class Sms(Notifier):
    channel = "sms"

    def send(self, to: str, body: str) -> None:
        first = body.splitlines()[0].strip() if body else ""
        print(f"  [sms] → {to}: {first} ……")
