import sys


def main(argv=None) -> int:
    argv = list(sys.argv[1:]) if argv is None else argv

    if "--cli" in argv:
        argv.remove("--cli")
        from cli.app import run_cli
        return run_cli(argv)
    try:
        from gui.app import run_gui
    except ImportError as e:
        print(f"无法启动图形界面：{e}", file=sys.stderr)
        print("请先安装 PySide6：pip install PySide6", file=sys.stderr)
        return 1
    return run_gui()


if __name__ == "__main__":
    sys.exit(main())
