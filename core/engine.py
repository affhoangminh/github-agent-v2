import importlib


def parse_counter(raw, parser_name):
    try:
        print("👉 Load parser:", parser_name)

        module = importlib.import_module(f"core.parsers.{parser_name}")

        if not hasattr(module, "parse"):
            raise Exception("Parser thiếu hàm parse()")

        result = module.parse(raw)

        print("👉 Parse result:", result)

        return result

    except Exception as e:
        print("❌ Parser error:", e)
        return {}