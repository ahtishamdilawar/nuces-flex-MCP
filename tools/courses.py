from tools.mcp_instance import mcp
from auth import ensure_logged_in
from parsers.courses import parse_courses


@mcp.tool()
def get_courses() -> dict:
    """
    Get registered courses for current semester.
    
    Returns:
        Dictionary with courses containing:
        - code, name, section, credits, instructor
    """
    try:
        session = ensure_logged_in()
        html = session.get_html("/Student/CourseRegistration")
        result = parse_courses(html)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
