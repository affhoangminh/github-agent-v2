import importlib


def parse_counter(raw, parser_name):
    try:
        module = importlib.import_module(f"core.parsers.{parser_name}")

        if not hasattr(module, "parse"):
            raise Exception("Parser thiếu hàm parse()")

        return module.parse(raw)

    except Exception as e:
        print("❌ Parser error:", e)
        return {}