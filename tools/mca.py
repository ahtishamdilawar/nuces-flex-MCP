from tools.mcp_instance import mcp
from auth import ensure_logged_in, BASE_URL


@mcp.tool()
def get_mca(offer_id: str) -> dict:
    """
    Get Modified Class Average (MCA) for a course.
    
    MCA is used for relative grading in courses (mostly electives).
    The offer_id can be obtained from get_transcript() for courses 
    where has_mca is True.
    
    Args:
        offer_id: The course offer ID (e.g., "15202230205")
    
    Returns:
        Dictionary with grading scheme and MCA value.
    """
    try:
        session = ensure_logged_in()
        
        # Make POST request to API endpoint
        response = session.client.post(
            f"{BASE_URL}/Student/Populate_GradeSchemeDetails",
            data={"OfferId": offer_id}
        )
        response.raise_for_status()
        
        data = response.json()
        
        result = {
            "grading_schemes": []
        }
        
        for item in data:
            if item.get("GRADING_FACTOR", 0) != 0:
                result["grading_schemes"].append({
                    "scheme": item.get("GS_TEXT", ""),
                    "mca": item.get("GRADING_FACTOR", 0)
                })
        
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
