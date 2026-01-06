from typing import Any
from parsers.fees import parse_fee_report


def parse_challan(html: str) -> dict[str, Any]:
    return parse_fee_report(html)
