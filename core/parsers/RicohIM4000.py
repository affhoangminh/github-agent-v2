import re


def extract_between(raw, start, end):
    match = re.search(start + r"(.*?)" + end, raw, re.S | re.I)
    return match.group(1) if match else ""


def extract_td_numbers(block):
    numbers = re.findall(r"<td[^>]*>\s*([\d,]+)\s*</td>", block, re.I)
    numbers = [int(n.replace(",", "")) for n in numbers]
    return numbers


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

    # TOTAL
    total_match = re.search(
        r"Total Counter.*?<td[^>]*>([\d,]+)</td>",
        raw, re.S | re.I
    )
    if total_match:
        result["total"] = int(total_match.group(1).replace(",", ""))

    # COPIER
    copier_section = extract_between(raw, "Copier", "Printer")
    nums = extract_td_numbers(copier_section)
    if nums:
        result["copy"] = nums[0]

    # PRINTER
    printer_section = extract_between(raw, "Printer", "Fax")
    nums = extract_td_numbers(printer_section)
    if nums:
        result["printer"] = nums[0]

    # SCAN
    scan_section = extract_between(raw, "Scanner Send", "Coverage")
    nums = extract_td_numbers(scan_section)
    if nums:
        result["scan"] = nums[-1]

    result["bw"] = result["total"]
    result["color"] = 0

    return result