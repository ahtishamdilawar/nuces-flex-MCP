from typing import Any
from bs4 import BeautifulSoup
import re


def parse_attendance(html: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    
    result = {"courses": []}
    
    all_h5 = soup.find_all("h5")
    course_headers = []
    percentages = []
    
    for h5 in all_h5:
        text = h5.get_text(strip=True)
        if re.match(r"[A-Z]{2}\d+-.+", text):
            course_headers.append(text)
        elif re.match(r"\d+\.\d+%", text):
            percentages.append(text)
    
    tables = soup.find_all("table")
    attendance_tables = []
    
    for table in tables:
        headers = [th.get_text(strip=True) for th in table.find_all("th")]
        if "Lecture No" in headers or "Date" in headers:
            attendance_tables.append(table)
    
    for i, table in enumerate(attendance_tables):
        course_name = course_headers[i] if i < len(course_headers) else f"Course {i+1}"
        percentage = percentages[i] if i < len(percentages) else None
        
        course_match = re.match(r"([A-Z]{2}\d+)-(.+?)\s*\(([^)]+)\)", course_name)
        
        course_data = {
            "course_code": course_match.group(1) if course_match else "",
            "course_name": course_match.group(2).strip() if course_match else course_name,
            "section": course_match.group(3) if course_match else "",
            "attendance_percentage": percentage,
            "lectures": []
        }
        
        for row in table.find_all("tr"):
            cols = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(cols) >= 4:
                course_data["lectures"].append({
                    "lecture_no": cols[0],
                    "date": cols[1],
                    "duration_hours": cols[2],
                    "presence": cols[3]
                })
        
        result["courses"].append(course_data)
    
    return result
