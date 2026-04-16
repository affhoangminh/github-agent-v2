import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def get_value(soup, element_id):
    el = soup.find(id=element_id)
    if el:
        try:
            return int(el.text.strip())
        except ValueError as e:
            logger.error("Cannot parse int from element '%s': %s", element_id, e)
            return 0
    return 0


def parse(html):
    logger.debug("Running parser: Toshiba3518")

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

    logger.debug("Toshiba3518 result: %s", result)

    return result