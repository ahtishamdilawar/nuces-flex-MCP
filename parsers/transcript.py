from typing import Any
from bs4 import BeautifulSoup
import re


def parse_transcript(html: str) -> dict[str, Any]:
    """Parse transcript page HTML.
    
    Structure: Each semester is in a col-md-6 div with:
    - h5 with semester name (e.g., "Fall 2022")
    - pull-right div with spans: Cr. Att, Cr. Ernd, CGPA, SGPA
    - table with courses
    """
    soup = BeautifulSoup(html, "html.parser")
    
    result = {"semesters": [], "cgpa": None, "student_info": {}}
    
    # Extract student info from header
    student_info_div = soup.find("div", class_="m-portlet__body")
    if student_info_div:
        for span in student_info_div.find_all("span"):
            text = span.get_text(strip=True)
            if text.startswith("ARN:"):
                result["student_info"]["arn"] = text.replace("ARN:", "").strip()
            elif text.startswith("Roll No:"):
                result["student_info"]["roll_no"] = text.replace("Roll No:", "").strip()
            elif text.startswith("Name:"):
                result["student_info"]["name"] = text.replace("Name:", "").strip()
            elif text.startswith("Batch:"):
                result["student_info"]["batch"] = text.replace("Batch:", "").strip()
    
    # Find all semester sections (col-md-6 divs containing tables)
    semester_sections = soup.find_all("div", class_="col-md-6")
    
    for section in semester_sections:
        # Find semester name from h5
        h5 = section.find("h5")
        if not h5:
            continue
        
        semester_name = h5.get_text(strip=True)
        if not re.match(r"(Fall|Spring|Summer)\s+\d{4}", semester_name):
            continue
        
        semester_data = {
            "name": semester_name,
            "credits_attempted": None,
            "credits_earned": None,
            "cgpa": None,
            "sgpa": None,
            "courses": []
        }
        
        # Extract stats from pull-right div
        pull_right = section.find("div", class_="pull-right")
        if pull_right:
            stats_text = pull_right.get_text()
            
            cr_att = re.search(r"Cr\.\s*Att:\s*(\d+)", stats_text)
            if cr_att:
                semester_data["credits_attempted"] = int(cr_att.group(1))
            
            cr_ernd = re.search(r"Cr\.\s*Ernd:\s*(\d+)", stats_text)
            if cr_ernd:
                semester_data["credits_earned"] = int(cr_ernd.group(1))
            
            cgpa = re.search(r"CGPA:\s*(\d+\.?\d*)", stats_text)
            if cgpa:
                semester_data["cgpa"] = float(cgpa.group(1))
            
            sgpa = re.search(r"SGPA:\s*(\d+\.?\d*)", stats_text)
            if sgpa:
                semester_data["sgpa"] = float(sgpa.group(1))
        
        # Parse courses table
        table = section.find("table")
        if table:
            for row in table.find_all("tr"):
                tds = row.find_all("td")
                if len(tds) < 5:
                    continue
                
                cols = [td.get_text(strip=True) for td in tds]
                
                offer_id = None
                has_mca = False
                
                first_td = tds[0]
                link = first_td.find("a", onclick=True)
                if link:
                    onclick = link.get("onclick", "")
                    match = re.search(r"fn_StdGradeSchemeDetail\((\d+)\)", onclick)
                    if match:
                        offer_id = match.group(1)
                        has_mca = True
                
                course_type = cols[6] if len(cols) > 6 else ""
                
                semester_data["courses"].append({
                    "code": cols[0],
                    "name": cols[1],
                    "section": cols[2] if len(cols) > 2 else "",
                    "credit_hours": cols[3] if len(cols) > 3 else "",
                    "grade": cols[4] if len(cols) > 4 else "",
                    "points": cols[5] if len(cols) > 5 else "",
                    "type": course_type,  # "Core" or "Elective"
                    "remarks": cols[7] if len(cols) > 7 else "",
                    "offer_id": offer_id,  # For fetching MCA
                    "has_mca": has_mca  # True if uses relative grading (MCA)
                })
        
        if semester_data["courses"]:
            result["semesters"].append(semester_data)
    
    # Get final CGPA from the last semester
    if result["semesters"]:
        result["cgpa"] = result["semesters"][-1].get("cgpa")
    
    return result
