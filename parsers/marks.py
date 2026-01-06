from typing import Any
from bs4 import BeautifulSoup
import re


def parse_marks(html: str) -> dict[str, Any]:
    """Parse marks page HTML with tab-pane and card structure."""
    soup = BeautifulSoup(html, "html.parser")
    
    result = {"courses": []}
    
    tab_panes = soup.find_all("div", class_="tab-pane")
    
    for pane in tab_panes:
        course_header = pane.find("h5")
        if not course_header:
            continue
            
        header_text = course_header.get_text(strip=True)
        course_match = re.match(r"([A-Z]{2}\d+)-(.+?)\s*\(([^)]+)\)", header_text)
        
        if not course_match:
            continue
            
        course_data = {
            "course_code": course_match.group(1),
            "course_name": course_match.group(2).strip(),
            "section": course_match.group(3),
            "assessments": {}
        }
        
        cards = pane.find_all("div", class_="card")
        
        for card in cards:
            button = card.find("button")
            if not button:
                continue
                
            assessment_type = button.get_text(strip=True)
            
            if "Grand Total" in assessment_type:
                continue
            
            table = card.find("table")
            if not table:
                continue
            
            items = []
            for row in table.find_all("tr"):
                if "Total" in row.get_text()[:10]:
                    continue
                cols = [td.get_text(strip=True) for td in row.find_all("td")]
                if len(cols) >= 4:
                    items.append({
                        "number": cols[0],
                        "weightage": cols[1],
                        "obtained_marks": cols[2],
                        "total_marks": cols[3],
                        "average": cols[4] if len(cols) > 4 else "",
                        "min": cols[6] if len(cols) > 6 else "",
                        "max": cols[7] if len(cols) > 7 else ""
                    })
            
            if items:
                course_data["assessments"][assessment_type] = items
        
        if course_data["assessments"]:
            result["courses"].append(course_data)
    
    return result
