"""最外层入口：python main.py

注意 IMPORT_LOG：每个包的 __init__.py 被执行的那一刻会往里追加自己的名字，
所以最后打印出来的顺序，就是「谁把谁拉起来了」的真实顺序。
"""

from shop import IMPORT_LOG, __version__
from shop.run import demo

if __name__ == "__main__":
    demo()
    print(f"\nshop v{__version__} · 包被导入的顺序：")
    for name in IMPORT_LOG:
        print("   →", name)
