from typing import Optional
from tools.mcp_instance import mcp
from auth import ensure_logged_in
from parsers.attendance import parse_attendance


@mcp.tool()
def get_attendance(semester_id: Optional[str] = None) -> dict:
    """
    Get attendance data for all courses.
    
    Args:
        semester_id: Optional semester ID (e.g., '20253' for Fall 2025). 
                     Format: YYYY + (1=spring, 2=summer, 3=fall)
    
    Returns:
        Dictionary with courses containing:
        - course_code, course_name, section
        - attendance_percentage
        - lectures (list with date, presence P/A)
    """
    try:
        session = ensure_logged_in()
        
        path = "/Student/StudentAttendance"
        if semester_id:
            path += f"?semid={semester_id}"
        
        html = session.get_html(path)
        result = parse_attendance(html)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
