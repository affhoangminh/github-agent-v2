import requests
import logging

logger = logging.getLogger(__name__)

def fetch(url):
    """Tải dữ liệu HTML bằng thư viện requests (Nhanh, cho các trang tĩnh)."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)

        if res.status_code != 200:
            logger.error("HTTP error %s for URL: %s", res.status_code, url)
            return None

        return res.text

    except requests.RequestException as e:
        logger.error("Requests error for %s: %s", url, e)
        return None
