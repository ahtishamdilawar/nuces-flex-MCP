from tools.mcp_instance import mcp
from auth import ensure_logged_in


@mcp.tool()
def login() -> str:
    """
    Login to FLEX Student Portal.
    Opens a browser window for automatic reCAPTCHA handling.
    Credentials are read from FLEX_ROLL_NO and FLEX_PASSWORD environment variables.
    
    Returns:
        Success or failure message.
    """
    try:
        session = ensure_logged_in()
        return "Successfully logged in to FLEX Student Portal!"
    except Exception as e:
        return f"Login failed: {str(e)}"
