from tools.mcp_instance import mcp

# Import all tools to register them with the MCP instance
import tools.login
import tools.attendance
import tools.marks
import tools.transcript
import tools.mca
import tools.courses
import tools.fees
import tools.status


if __name__ == "__main__":
    mcp.run()
