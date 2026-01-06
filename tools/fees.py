from tools.mcp_instance import mcp
from auth import ensure_logged_in
from parsers.fees import parse_fee_report


@mcp.tool()
def get_fee_report() -> dict:
    """
    Get consolidated fee report with payment history.
    
    Returns:
        Dictionary with:
        - payments: List of payment records with semester, amount, challan_no, 
                    due_date, payment_date, status
        - pending: List of pending fee items
    """
    try:
        session = ensure_logged_in()
        html = session.get_html("/ConsolidatedFeeReport/ConsolidatedStdFeeReport")
        result = parse_fee_report(html)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
