"""通知渠道的公共基类。

它不认识 orders，也不认识 catalog——所以任何渠道模块引它都不会产生环。
"""


class Notifier:
    channel = "?"

    def send(self, to: str, body: str) -> None:
        raise NotImplementedError
