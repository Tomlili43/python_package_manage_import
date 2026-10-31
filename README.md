# import_lab · 看懂包之间怎么互相引用

一个刻意做小、刻意做深的项目：**3 层包 + 跨分支互引**，总共约 200 行代码。
目的是把 import 的四件事一次看清：

1. 绝对导入 vs 相对导入（`..` 和 `...` 到底数到第几层）
2. `__init__.py` 当门面用，调用方不必知道文件藏在哪
3. 谁把谁拉起来了——`IMPORT_LOG` 会打印真实的加载顺序
4. 循环导入**到底什么时候才炸**（这个项目里能亲手复现一次）

## 目录：树的深度是 3 层

```
import_lab/
├── main.py                # 入口 A
├── run_cycle.py           # 入口 B：循环导入对照实验
├── shop/                  ← 第 1 层
│   ├── __init__.py        # 版本号 + IMPORT_LOG，刻意不 import 子包
│   ├── __main__.py        # 让 `python -m shop` 也能跑
│   ├── run.py             # 演示流程，两个入口共用
│   ├── catalog/           ← 第 2 层
│   │   ├── __init__.py    # 门面：from .books.models import Book
│   │   ├── base.py        # 依赖图的叶子：不欠任何人
│   │   └── books/         ← 第 3 层
│   │       ├── __init__.py
│   │       ├── models.py  # 相对导入（..base / ...）
│   │       └── pricing.py # 绝对导入
│   ├── orders/            ← 第 2 层
│   │   ├── __init__.py    # 门面：from .cart import Cart
│   │   ├── cart.py        # 跨分支相对导入 + 函数内延迟导入
│   │   └── receipt.py     # 跨分支绝对导入
│   └── notify/            ← 第 2 层
│       ├── __init__.py
│       ├── base.py
│       └── channels/      ← 第 3 层
│           ├── __init__.py
│           ├── emailer.py # 3 个点跨回 orders
│           └── sms.py
└── cycle_demo/            # 独立的最小循环导入复现（和 shop 无关）
```

## 依赖图：谁 import 谁

```
shop/catalog/base.py           ← 叶子，谁都引它，它不欠任何人
        ↑            ↑
   (..base)      (绝对)
        |            |
shop/catalog/books/models.py ←──── shop/orders/cart.py
        ↑   (绝对)                      │  (相对 .receipt)
        |                               ↓
shop/catalog/books/pricing.py ←──── shop/orders/receipt.py
                                        ↑  (...orders.receipt，3 个点)
                                        │
                              shop/notify/channels/emailer.py
                                        ↑  (cart.checkout() 里延迟导入)
                              shop/orders/cart.py ─ ─ ─ ┘（虚线=运行时才发生）

shop/notify/channels/sms.py  → shop/notify/base.py   （只认自己这一支）
```

## 四种写法，分别在哪个文件里

| 写法 | 出现位置 | 说明 |
| --- | --- | --- |
| 绝对导入 | `books/pricing.py`、`orders/receipt.py` | 从最外层包写起，路径和文件在第几层无关 |
| 相对 `..`（上一层包） | `books/models.py` → `..base` | 回到 catalog |
| 相对 `...`（上两层包） | `books/models.py` → `from ... import`、 `channels/emailer.py` → `...orders.receipt` | 先爬到 shop，再下到另一根树枝 |
| 函数内延迟导入 | `orders/cart.py` 的 `checkout()` | 运行时才加载，切断整条加载链 |

**点怎么数**：站在 `shop/catalog/books/models.py` 看——
`.` = books，`..` = catalog，`...` = shop。点的个数就是**往树根爬几级**，跟文件自己在第几层无关。

## 跑起来

```bash
python main.py      # 或 python -m shop
python run_cycle.py # 循环导入对照实验
```

`python main.py` 最后会打印真实的加载顺序（`emailer` 排在最后，因为它是延迟导入）：

```
shop v1.0 · 包被导入的顺序：
   → shop
   → shop.catalog
   → shop.catalog.books
   → shop.catalog.books.models
   → shop.orders
   → shop.catalog.books.pricing
   → shop.orders.receipt
   → shop.orders.cart
   → shop.notify
   → shop.notify.channels
   → shop.notify.channels.sms
   → shop.run
   → shop.notify.channels.emailer        ← 结账那一刻才被拉起来
```

### 三种运行方式的区别

| 命令 | 结果 |
| --- | --- |
| `python main.py` | ✅ 正常 |
| `python -m shop` | ✅ 正常，走 `shop/__main__.py` |
| `python shop/run.py` | ❌ `ModuleNotFoundError: No module named 'shop'` |

第三个为什么不行：直接跑文件时，`sys.path[0]` 是 `shop/` 这一层，而不是项目根，
解释器根本找不到叫 `shop` 的包。包内的文件要从**项目根**启动，而不是从文件自己所在目录启动。

## 循环导入：什么时候真的会炸

这一点网上的说法经常是错的，本项目实测结论：

| 写法 | 结果 |
| --- | --- |
| `from ...orders.receipt import render_receipt`（引**子模块**） | ✅ 不报错。父包初始化一半时，子模块照样能加载 |
| `from ...orders import Cart`（引包 `__init__.py` 里 re-export 的**名字**） | ❌ `ImportError: cannot import name 'Cart' from partially initialized module 'shop.orders' (most likely due to a circular import)` |
| 两个模块在顶层互相 import 对方的**名字** | ❌ 见 `cycle_demo/`，`run_cycle.py` 会打印真实报错 |

规律：**引「模块」安全，引「还没执行到的名字」危险**。
所以 `cart.py` 里那句延迟导入的真实作用是「别让 notify 整条链在 `import cart` 时就被拉起来」，
而不是「不这么写就会崩」。

## 动手实验

1. 把 `cart.py` 里 `checkout()` 的 `from ..notify.channels.emailer import Emailer` 挪到文件顶部 →
   程序照样跑通，但 `IMPORT_LOG` 里 `emailer` 的位置会提前到 `cart` 之前。
2. 把 `emailer.py` 的 `from ...orders.receipt import render_receipt` 改成 `from ...orders import Cart`
   → 复现上表第二行的真实报错。
3. 删掉 `catalog/__init__.py` 里的 `from .books.models import Book` →
   `run.py` 的 `from shop.catalog import Book` 立刻失败，体会「门面」的价值。
4. 在 `shop/__init__.py` 加一行 `from . import catalog` →
   从此 `import shop` 就会把整棵树拉起来，`IMPORT_LOG` 变长。这就是「顶层包该不该偷懒」的取舍。

## 配套面试题

`INTERVIEW.md`：20 道基础/进阶题 + 4 道场景题 + 3 道动手题，每题都标了在这个项目里怎么验证。
题目围绕「包与模块导入」这一块，答案全部实测过——尤其是循环导入那几道，网上常见的说法是错的。
