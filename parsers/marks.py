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
            "assessments": {},
            "total_obtained": 0.0,
            "total_weightage": 0.0
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
            
            assessment_data = {
                "items": [],
                "total_weightage": None,
                "total_obtained": None
            }
            
            # Parse data rows (class="calculationrow")
            for row in table.find_all("tr", class_="calculationrow"):
                cols = [td.get_text(strip=True) for td in row.find_all("td")]
                if len(cols) >= 4:
                    # Handle "-" for missing marks
                    obtained = cols[2] if cols[2] != "-" else None
                    
                    assessment_data["items"].append({
                        "number": cols[0],
                        "weightage": _parse_float(cols[1]),
                        "obtained_marks": _parse_float(obtained) if obtained else None,
                        "total_marks": _parse_float(cols[3]),
                        "average": _parse_float(cols[4]) if len(cols) > 4 else None,
                        "std_dev": cols[5].strip() if len(cols) > 5 and cols[5].strip() else None,
                        "min": _parse_float(cols[6]) if len(cols) > 6 else None,
                        "max": _parse_float(cols[7]) if len(cols) > 7 else None
                    })
            
            # Parse total row (has totalCol* classes)
            total_row = table.find("tr", class_=re.compile(r"totalColumn"))
            if not total_row:
                # Also check tfoot
                tfoot = table.find("tfoot")
                if tfoot:
                    total_row = tfoot.find("tr")
            
            if total_row:
                weightage_td = total_row.find("td", class_="totalColweightage")
                obtained_td = total_row.find("td", class_="totalColObtMarks")
                
                if weightage_td:
                    assessment_data["total_weightage"] = _parse_float(weightage_td.get_text(strip=True))
                if obtained_td:
                    assessment_data["total_obtained"] = _parse_float(obtained_td.get_text(strip=True))
                    
                # Add to course totals
                if assessment_data["total_weightage"]:
                    course_data["total_weightage"] += assessment_data["total_weightage"]
                if assessment_data["total_obtained"]:
                    course_data["total_obtained"] += assessment_data["total_obtained"]
            
            if assessment_data["items"]:
                course_data["assessments"][assessment_type] = assessment_data
        
        if course_data["assessments"]:
            result["courses"].append(course_data)
    
    return result


def _parse_float(value: str) -> float | None:
    """Parse a string to float, returning None if invalid."""
    if value is None:
        return None
    try:
        # Remove any whitespace
        value = value.strip()
        if not value or value == "-":
            return None
        return float(value)
    except (ValueError, TypeError):
        return None
