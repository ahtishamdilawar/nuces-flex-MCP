from typing import Any
from bs4 import BeautifulSoup


def parse_fee_report(html: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    
    result = {"payments": []}
    
    # Try to find by specific ID first
    table = soup.find("table", id="sample_CollectionDetail")
    
    if not table:
        for t in soup.find_all("table"):
            headers = [th.get_text(strip=True) for th in t.find_all("th")]
            if len(headers) >= 10 and "Semester" in headers and "Amount" in headers:
                table = t
                break
    
    if not table:
        return result
    
    # Parse tbody rows
    tbody = table.find("tbody")
    if tbody:
        rows = tbody.find_all("tr")
        for row in rows:
            cols = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(cols) >= 10:
                result["payments"].append({
                    "sr_no": cols[0],
                    "semester": cols[1],
                    "challan_no": cols[2],
                    "instrument_type": cols[3],
                    "instrument_no": cols[4],
                    "amount": cols[5],
                    "due_date": cols[6],
                    "payment_date": cols[7],
                    "entered_by": cols[8],
                    "status": cols[9]
                })
    
    return result
