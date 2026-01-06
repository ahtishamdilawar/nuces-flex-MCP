from typing import Any
from bs4 import BeautifulSoup
import re


def parse_courses(html: str) -> dict[str, Any]:
    """Parse course registration page HTML."""
    soup = BeautifulSoup(html, "html.parser")
    
    result = {"courses": []}
    
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cols = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(cols) >= 2 and re.match(r"[A-Z]{2}\d+", cols[0]):
                result["courses"].append({
                    "code": cols[0],
                    "name": cols[1],
                    "section": cols[2] if len(cols) > 2 else "",
                    "credits": cols[3] if len(cols) > 3 else "",
                    "instructor": cols[4] if len(cols) > 4 else ""
                })
    
    return result
