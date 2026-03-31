import importlib


def parse_counter(html, parser_name):
    print("👉 Load parser:", parser_name)

    try:
        # =========================
        # import module theo tên
        # =========================
        module_path = f"core.parsers.{parser_name}"
        module = importlib.import_module(module_path)

        # =========================
        # tìm function parse
        # =========================
        if hasattr(module, "parse"):
            return module.parse(html)

        elif hasattr(module, "parse_counter"):
            return module.parse_counter(html)

        elif hasattr(module, "run"):
            return module.run(html)

        else:
            raise Exception(f"No parse function in {parser_name}")

    except Exception as e:
        print("❌ Parser error:", e)

        return {
            "total": 0,
            "bw": 0,
            "color": 0,
            "copy": 0,
            "printer": 0,
            "scan": 0
        }