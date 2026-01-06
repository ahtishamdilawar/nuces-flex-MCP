from tools.mcp_instance import mcp
from auth import ensure_logged_in
from parsers.transcript import parse_transcript


@mcp.tool()
def get_transcript() -> dict:
    """
    Get full academic transcript with all semesters.
    
    Grading System:
    - Core courses: Use absolute grading (fixed grade boundaries)
    - Elective courses: Use relative grading with MCA (Modified Class Average)
      - Courses with has_mca=True have an offer_id to fetch MCA details
    
    Returns:
        Dictionary with:
        - student_info: ARN, Roll No, Name, Batch
        - semesters: List with each semester containing:
          - name, credits_attempted, credits_earned, cgpa, sgpa
          - courses: code, name, grade, credit_hours, points, type, offer_id, has_mca
        - cgpa: Final cumulative GPA
    """
    try:
        session = ensure_logged_in()
        html = session.get_html("/Student/Transcript")
        result = parse_transcript(html)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
