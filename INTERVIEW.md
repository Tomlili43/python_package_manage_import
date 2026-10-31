# 包与模块导入 · 面试题集

配套 `import_lab/`。每题都标了**在项目里怎么验证**——答不上来就跑一次，比背答案牢。
所有"实测结论"都是在这个项目上真跑出来的，不是抄的。

---

## 一、基础题

### Q1 `import a.b.c` 和 `from a.b import c` 有什么区别？

- `import a.b.c`：把**顶层名字 `a`** 绑到当前命名空间，用的时候要写全 `a.b.c.x`。
  父包 `a`、`a.b` 都会被依次导入并执行。
- `from a.b import c`：把 `c` 直接绑定进来。`c` 可能是子模块，也可能是模块里的任意属性。
- 两者的 `sys.modules` **完全一样**（`a`、`a.b`、`a.b.c` 都在），差别只在当前命名空间多出哪个名字。

> 追问：`from a import b.c` 合法吗？→ 不合法，`from` 后面只能是模块，`import` 后面只能是不带点的名字。

### Q2 同一个模块被 import 两次，模块体会执行几次？

一次。第一次导入时模块体执行，结果存进 `sys.modules`；之后再 import 直接取缓存，不执行。
所以**模块级的副作用（打印、写文件、改全局）只会发生一次**。

> 验证：`import shop.catalog` 后再 `import shop.catalog`，`IMPORT_LOG` 不会变长。

### Q3 `__init__.py` 是必须的吗？没有会怎样？

Python 3.3+ 不是必须的（PEP 420 命名空间包）：没有 `__init__.py` 的目录仍可被 import，
但它是"命名空间包"——`__file__` 为 `None`、`__spec__.origin` 为 `None`、`__path__` 仍存在。

实测（`demo/` 下只有 `mod.py`，无 `__init__.py`）：

```
demo.__file__        → None
demo.__spec__.origin → None
demo.mod.VALUE       → 'no __init__ here'   # 照样能 import
```

> 追问：那为什么还要写 `__init__.py`？→ 需要执行初始化代码、做 re-export 门面、控制 `__all__`、
> 或者需要打包工具把它识别为常规包时，就必须要。

### Q4 `__init__.py` 有什么用？说三个

1. **包初始化**：import 包时执行（本项目用它往 `IMPORT_LOG` 追加名字）
2. **门面 / re-export**：`catalog/__init__.py` 里 `from .books.models import Book`，
   于是调用方写 `from shop.catalog import Book` 就行，不用知道文件藏在第三层
3. **定义 `__all__`**：控制 `from pkg import *` 的导出范围

### Q5 相对导入的点怎么数？

站在**当前模块**看：`.` = 自己所在包，`..` = 上一层包，`...` = 上两层包，以此类推。
点的个数 = 往树根爬几级，和文件在第几层无关。

在 `shop/catalog/books/models.py` 里：

```python
from ..base import Item, money   # .. → shop.catalog.base
from ... import __version__      # ... → shop
```

> 易错：点在**包**上数，不是在目录上数；模块自己不算一级。

### Q6 `import shop` 之后，能访问 `shop.catalog` 吗？

**不能**，除非别处 import 过 `shop.catalog`。

```
>>> import shop
>>> shop.catalog
AttributeError: module 'shop' has no attribute 'catalog'
>>> import shop.catalog      # 这一次导入会把 catalog 挂成 shop 的属性
>>> shop.catalog
<module 'shop.catalog' ...>
```

原因：`import shop` 只执行 `shop/__init__.py`，它没 import 子包，所以子包既不在 `sys.modules`、
也不会被自动挂成属性。子模块被导入后，Python 才会把它设为父包的属性——**这就是"导入有副作用"的直接证据**。

### Q7 `if __name__ == "__main__"` 解决什么问题？

模块被 import 时 `__name__` 是模块全名；被直接运行时是 `"__main__"`。
这个判断让文件既能当库被 import（不执行演示代码），又能当脚本直接跑。
本项目里 `main.py`、`run_cycle.py`、`shop/__main__.py` 都用了。

### Q8 `python main.py` 和 `python -m shop` 有什么不同？

| | `python main.py` | `python -m shop` |
| --- | --- | --- |
| `sys.path[0]` | 脚本所在目录（项目根） | 当前工作目录 |
| 谁当 `__main__` | `main.py` | `shop/__main__.py` |
| 父包是否先导入 | 否 | 是（`shop/__init__.py` 先执行） |

两者在本项目里都能跑通，因为项目根都在搜索路径上。

### Q9 为什么 `python shop/run.py` 会报 `No module named 'shop'`？

直接运行文件时，`sys.path[0]` 被设成**该文件所在目录**（`shop/`），而不是项目根。
于是解释器在 `shop/` 下面找名为 `shop` 的包，找不到。

> 结论：包里的模块要从**项目根**启动（`python main.py`、`python -m shop`），
> 或者把项目根加进 `PYTHONPATH`。这条能顺带解释一堆"本地能跑、CI 上挂"的诡异问题。

### Q10 `__all__` 到底限制了什么？

**只限制 `from pkg import *`**，不影响显式导入。

```
shop.catalog.__all__ = ['Book']   →  from shop.catalog import *  只拿到 Book
                                     from shop.catalog import cart  依然可以
```

> 易错：很多人以为 `__all__` 能"禁止外部导入"——不能。想表达私有就用下划线前缀。

### Q11 `sys.path` 是怎么拼出来的？

1. `sys.path[0]`：脚本所在目录（直接跑文件时）或当前目录（`-m` / `-c` / 交互）
2. `PYTHONPATH` 环境变量里的路径
3. 标准库目录
4. `site-packages`（由 `site` 模块加入，含 `.pth` 引入的路径）

按顺序查找，先命中先得——同名模块被谁抢到，取决于这个顺序。

### Q12 `__pycache__` 里的 `.pyc` 是什么？能删吗？

模块编译后的字节码缓存，下次 import 时若源码没变就跳过编译，加快导入。
**可以随便删**，删了会自动重建（`python -B` 可禁止生成）。
注意它只是缓存，不参与版本管理（应进 `.gitignore`）。

---

## 二、进阶题

### Q13 循环导入什么时候**真的**会炸？

关键区分：引**模块**安全，引**还没执行到的名字**危险。

| 写法 | 结果 |
| --- | --- |
| `from ...orders.receipt import render_receipt`（引子模块） | ✅ 不报错。父包半初始化时，子模块照样能加载 |
| `from ...orders import Cart`（引包 `__init__.py` re-export 的名字） | ❌ `ImportError: cannot import name 'Cart' from partially initialized module 'shop.orders' (most likely due to a circular import)` |
| 两个模块顶层互引对方的名字 | ❌ 见 `cycle_demo/`，`python run_cycle.py` 可复现 |

> 这是最容易讲错的一题。很多人以为"只要成环就崩"，实测并非如此。

### Q14 循环导入怎么修？（至少说三种）

1. **延迟导入**：把 import 放进函数体，用到时才拿（`cart.checkout()` 就是这么做的）
2. **下沉公共依赖**：两边都要的东西抽到独立的底层模块（本项目的 `notify/base.py`、`catalog/base.py` 就是这个思路——谁都引它，它不欠任何人）
3. **引模块不引名字**：`import pkg.mod` 代替 `from pkg import name`
4. **合并模块**：如果两个模块必须互相知道对方的一切，说明拆错了

### Q15 `python -m shop.orders.cart` 为什么会有 RuntimeWarning？

实测：

```
RuntimeWarning: 'shop.orders.cart' found in sys.modules after import of package
'shop.orders', but prior to execution of 'shop.orders.cart';
this may result in unpredictable behaviour
```

因为 `orders/__init__.py` 里写了 `from .cart import Cart`。
`-m` 会先导入父包 `shop.orders`——此时 `cart` 已经作为普通模块进过 `sys.modules`；
接着 runpy 又要把 `cart` 当作 `__main__` 执行一遍。**同一个文件被执行两次**，
会产生两份类对象（`is` 比较为假、`isinstance` 失效）。

> 教训：包的 `__init__.py` 里 re-export 子模块，会让该子模块无法安全地用 `-m` 直接运行。

### Q16 相对导入为什么会报 `attempted relative import with no known parent package`？

相对导入靠 `__package__` 定位父包。脚本被**直接运行**时它是 `__main__`，`__package__` 为空，
解释器不知道"上一层包"是谁，于是报错。

```
$ python /tmp/relme.py        # 文件里只有 from . import sibling
ImportError: attempted relative import with no known parent package
```

> 结论：带相对导入的文件只能被 import，或用 `-m` 从包路径启动，不能直接当脚本跑。

### Q17 `importlib.reload()` 的坑是什么？

`reload` 只是**重新执行模块体**，模块对象本身还是同一个（不会新建），
但**别处已经绑定的旧引用不会更新**——它们仍指向重新执行前创建的对象。

实测：把 `pricing.TAX_RATE` 改成 `0.99` 再 reload，值回到源码里的 `0.06`；
而此前 `from ... import TAX_RATE` 拿走的那个副本，依旧是旧值。

> 所以 reload 适合调试单个模块，不适合当"热更新"机制。

### Q18 函数内延迟导入（lazy import）解决什么？代价是什么？

**解决**：① 切断加载链，`import cart` 不再顺带拉起整条 notify 链；
② 让可选依赖变成真可选（缺 SDK 时只有调用到才报错）；
③ 加快启动。
**代价**：导入错误延后到运行期才暴露；依赖关系在文件顶部看不见，可读性变差；
每次调用都有一次 `sys.modules` 查表（开销极小，通常可忽略）。

本项目里 `emailer` 在 `IMPORT_LOG` 里排在**最后一位**，就是它被延迟加载的证据。

### Q19 在顶层包的 `__init__.py` 里 import 子包，有什么代价？

`import shop` 从此会把整棵树拉起来——启动变慢、可选的第三方依赖变成必装、更容易制造环。
本项目 `shop/__init__.py` 刻意只放版本号和 `IMPORT_LOG`，就是这个取舍。

> 实验：给它加一行 `from . import catalog`，再看 `IMPORT_LOG` 变多长。

### Q20 同一个类通过"门面"和"完整路径"分别导入，是同一个对象吗？

是。`sys.modules` 保证模块单例，所以：

```python
from shop.catalog.books.models import Book as B1
from shop.catalog import Book as B2
B1 is B2   # True
```

> 反例见 Q15：一旦同一个文件被执行两次，就会有两份，`is` 变成 False。

---

## 三、读代码说结果（场景题）

### S1 下面这段会打印什么？

```python
import shop.catalog
print(shop.IMPORT_LOG)
```

答案：`['shop', 'shop.catalog', 'shop.catalog.books', 'shop.catalog.books.models']`

注意**没有 `pricing`**：`catalog/__init__.py` 的门面只 import 了 `models`。
导入是"按需发生"的，不是"扫目录全量加载"。

### S2 删掉 `catalog/__init__.py` 里的 `from .books.models import Book`，会怎样？

`run.py` 的 `from shop.catalog import Book` 立刻失败（`cannot import name 'Book'`）。
但 `from shop.catalog.books.models import Book` 仍然正常——门面只是一层便利，不是依赖本身。

### S3 把 `emailer.py` 的 `from ...orders.receipt import render_receipt` 换成 `from ...orders import Cart`，会怎样？

`ImportError: cannot import name 'Cart' from partially initialized module 'shop.orders' (most likely due to a circular import)`

原因是 `orders/__init__.py` 里有 `from .cart import Cart`，而 `cart` 又（在 Q18 的延迟导入路径上）
绕回 notify，形成环。改成引子模块 `orders.receipt` 就不炸——见 Q13。

### S4 以下三条命令，分别什么结果？

| 命令 | 结果 |
| --- | --- |
| `python main.py` | ✅ 正常，最后打印 13 项 `IMPORT_LOG` |
| `python -m shop` | ✅ 正常，走 `shop/__main__.py` |
| `python shop/run.py` | ❌ `ModuleNotFoundError: No module named 'shop'` |

---

## 四、动手题（适合当场写代码）

1. **加第 4 层**：在 `books/` 下再开一个包 `vip/`，让 `vip/pricing.py` 用相对导入拿到
   `books/models.py` 的 `Book`（需要几个点？）——考察点数与跨层引用。
2. **把延迟导入挪到顶部**：改 `cart.py`，跑一次，解释 `IMPORT_LOG` 里 `emailer` 位置的变化
   （提示：程序不会崩，只是顺序变了）。
3. **制造一次真正的循环导入**：让 `orders/__init__.py` 去 `from ..notify import base`，
   同时让 `notify/base.py` 反过来 `from ...orders import Cart`，观察报错信息，并说出两种修法。

---

## 五、面试官速查：哪些回答是"背的"，哪些是真懂

| 听上去对但不完整 | 完整答案 |
| --- | --- |
| "循环导入一定会报错" | 引子模块不报错，引未执行到的名字才报错（Q13） |
| "`__init__.py` 没用，Python 3 可以不要" | 命名空间包存在，但门面、初始化、`__all__` 都要靠它（Q3/Q4） |
| "import 多少次就执行多少次" | 只执行一次，`sys.modules` 缓存（Q2） |
| "`__all__` 能禁止外部导入" | 只影响 `import *`（Q10） |
| "相对导入的点按目录层数算" | 按包层级往上爬，模块自己不算一级（Q5） |
| "包内文件跑不起来是路径没配对" | 是 `sys.path[0]` 变成了文件所在目录（Q9） |
