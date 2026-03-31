from bs4 import BeautifulSoup


def get_value(soup, element_id):
    el = soup.find(id=element_id)
    if el:
        try:
            return int(el.text.strip())
        except:
            return 0
    return 0


def parse(html):
    print("🔥 PARSER TOSHIBA 3518")

    soup = BeautifulSoup(html, "lxml")

    total = get_value(soup, "Print_Total_TotalCounter_Total")
    bw = get_value(soup, "Print_Total_TotalCounter_Black")
    copy = get_value(soup, "Print_Total_CopyCounter_Total")
    printer = get_value(soup, "Print_Total_PrinterCounter_Total")
    scan = get_value(soup, "Scan_Total_TotalCounter_Total")

    result = {
        "total": total,
        "bw": bw if bw else total,
        "color": 0,
        "copy": copy,
        "printer": printer,
        "scan": scan,
    }

    print("👉 Toshiba result:", result)

    return result