from tools.mcp_instance import mcp
from auth import get_session


@mcp.tool()
def check_login_status() -> dict:
    """
    Check if currently logged in to FLEX portal.
    
    Returns:
        Dictionary with logged_in status and cookies_count.
    """
    session = get_session()
    return {
        "status": "success",
        "logged_in": session.is_logged_in(),
        "cookies_count": len(session.cookies) if session.cookies else 0
    }
