import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def _get_table_value(soup, block_class, row_label):
    """
    Lay gia tri tu bang counter trong Toshiba TopAccess SPA.

    Cau truc HTML:
      <div class="counter-content {block_class}-counter ...">
        <h5>Total Counter</h5>
        <table>
          <tbody>
            <tr><td class="labelled"></td><td class="labelled">Black</td><td class="labelled">Total</td></tr>
            <tr><td>Copy</td><td>21220</td><td>21220</td></tr>
            ...
            <tr><td>Total</td><td>22357</td><td>22357</td></tr>
          </tbody>
        </table>
      </div>

    Args:
        soup: BeautifulSoup object
        block_class: 'print' hoac 'scan'
        row_label: ten hang can lay, vi du 'Total', 'Copy', 'Printer'

    Returns:
        Gia tri cot cuoi (Total) cua hang do, hoac 0 neu khong tim thay.
    """
    try:
        # Tim div counter-content co class tuong ung
        block = soup.find("div", class_=f"{block_class}-counter")
        if not block:
            logger.warning("Counter block '%s-counter' not found", block_class)
            return 0

        # Tim bang dau tien trong block nay (Total Counter table)
        table = block.find("table")
        if not table:
            logger.warning("No table found in '%s-counter' block", block_class)
            return 0

        # Duyet tung hang, bo qua hang header (labelled)
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if not cells:
                continue
            # Bo qua hang header
            if cells[0].get("class") and "labelled" in cells[0].get("class"):
                continue
            # Kiem tra ten hang (cot dau tien)
            label = cells[0].get_text(strip=True)
            if label.lower() == row_label.lower():
                # Lay gia tri cot cuoi (Total)
                value_text = cells[-1].get_text(strip=True).replace(",", "")
                try:
                    return int(value_text)
                except ValueError:
                    logger.error(
                        "Cannot parse int from '%s' in %s-counter row '%s'",
                        value_text, block_class, row_label
                    )
                    return 0

        logger.warning("Row '%s' not found in '%s-counter'", row_label, block_class)
        return 0

    except Exception as e:
        logger.error("Error reading %s-counter row '%s': %s", block_class, row_label, e)
        return 0


def parse(html):
    logger.debug("Running parser: Toshiba2528")

    soup = BeautifulSoup(html, "lxml")

    # Kiem tra trang da render chua (phai co rightPane voi du lieu)
    right_pane = soup.find(id="rightPane")
    if not right_pane:
        logger.error("Toshiba2528: rightPane not found — page may not have rendered")
        return None

    # --- Print Counter ---
    # Lay tu bang Print Counter > Total Counter
    copy_print  = _get_table_value(soup, "print", "Copy")     # Copy (BW)
    fax_print   = _get_table_value(soup, "print", "Fax")      # Fax
    printer     = _get_table_value(soup, "print", "Printer")  # Printer
    list_print  = _get_table_value(soup, "print", "List")     # List
    total_print = _get_table_value(soup, "print", "Total")    # Print Total

    # --- Scan Counter ---
    scan_total  = _get_table_value(soup, "scan", "Total")     # Scan Total

    result = {
        "total":   total_print,
        "bw":      total_print,   # May nay chi co mau den trang
        "color":   0,
        "copy":    copy_print,
        "printer": printer,
        "scan":    scan_total,
    }

    logger.debug("Toshiba2528 result: %s", result)
    return result