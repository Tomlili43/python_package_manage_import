"""循环导入对照实验：python run_cycle.py"""

from cycle_demo import good_a


def main() -> None:
    print("--- 1) 顶层互相 import 名字：会炸")
    try:
        from cycle_demo import bad_a
    except ImportError as exc:
        print(f"  ImportError: {exc}")
    else:
        print("  ", bad_a.a())

    print("\n--- 2) 把 import 挪进函数：环就断了")
    print("  ", good_a.a2())


if __name__ == "__main__":
    main()
