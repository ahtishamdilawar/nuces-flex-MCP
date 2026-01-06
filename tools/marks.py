from tools.mcp_instance import mcp
from auth import ensure_logged_in
from parsers.marks import parse_marks


@mcp.tool()
def get_marks(semester_id: str) -> dict:
    """
    Get marks/grades for all courses.
    
    Args:
        semester_id: Must give semester ID (e.g., '20253' for Fall 2025).
                     Format: YYYY + (1=spring, 2=summer, 3=fall), Only works for latest years
                     Only works for latest years can't access old years marks
    
    Returns:
        Dictionary with courses containing:
        - course_code, course_name, section
        - assessments (Assignment, Quiz, Sessional-I, etc.)
        - Each assessment has: number, weightage, obtained_marks, total_marks, average
        - total absolutes can be calculated by adding the Total  of weightages for different assessments 
    """
    try:
        session = ensure_logged_in()
        
        path = "/Student/StudentMarks"
        if semester_id:
            path += f"?semid={semester_id}"
        
        html = session.get_html(path)
        result = parse_marks(html)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
