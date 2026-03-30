import re

def extract_between(raw, start, end):
    match = re.search(start + r"(.*?)" + end, raw, re.S | re.I)
    return match.group(1) if match else ""


def extract_number(block):
    match = re.search(r">([\d,]+)<", block)
    if match:
        return int(match.group(1).replace(",", ""))
    return 0


def parse(raw):
    result = {
        "total": 0,
        "bw": 0,
        "color": 0,
        "copy": 0,
        "printer": 0,
        "scan": 0
    }

    if not raw:
        return result

    # ================= TOTAL =================
    total_block = re.search(r"Total Counter.*?</tr>", raw, re.S | re.I)
    if total_block:
        result["total"] = extract_number(total_block.group(0))

    # ================= COPIER =================
    copier_section = extract_between(raw, "Copier", "Printer")
    if copier_section:
        result["copy"] = extract_number(copier_section)

    # ================= PRINTER =================
    printer_section = extract_between(raw, "Printer", "Fax")
    if printer_section:
        result["printer"] = extract_number(printer_section)

    # ================= SCAN =================
    scan_section = extract_between(raw, "Scanner Send", "Coverage")
    if scan_section:
        result["scan"] = extract_number(scan_section)

    # ================= BW =================
    result["bw"] = result["copy"] + result["printer"]

    return result