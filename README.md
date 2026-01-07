# FAST-NUCES flex Student Portal MCP Server

An MCP server that connects AI assistants like **Claude Desktop** or **GitHub Copilot** directly to your Flex Student Portal. Ask questions about your academic data in plain English.

## What Can You Do?

Once connected, just chat naturally:

| Ask This | Get This |
|-------------|-------------|
| *"Roast my transcript"* | A brutally honest AI review of your transcript |
| *"Am I passing PF?"* | Quick calculation of your current standing |
| *"How many classes did I bunk?"* | Attendance reality check |
| *"Compare my marks to class average"* | See where you stand vs classmates |

## Requirements

- **Python 3.11+**
- **Google Chrome** installed (for login automation)
- **Claude Desktop** or **GitHub Copilot** (with MCP support)

## Installation

1. **Clone and install dependencies:**
   ```bash
   git clone <repo-url>
   cd FLEX
   pip install -r requirements.txt
   ```

2. **Create `.env` file with your credentials:**
   ```env
   FLEX_ROLL_NO=22F-XXXX
   FLEX_PASSWORD=your_password
   ```

3. **Configure your MCP client:**

   <details>
   <summary><b>Claude Desktop</b></summary>

   Edit `%APPDATA%\Claude\claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "flex": {
         "command": "python",
         "args": ["C:/path/to/FLEX/server.py"],
         "env": {
           "FLEX_ROLL_NO": "22F-XXXX",
           "FLEX_PASSWORD": "your_password"
         }
       }
     }
   }
   ```
   </details>

   <details>
   <summary><b>GitHub Copilot</b></summary>

   Add to your MCP settings:
   ```json
   {
     "flex": {
       "command": "python",
       "args": ["C:/path/to/FLEX/server.py"]
     }
   }
   ```
   </details>

## Usage

1. Start your MCP client (Claude Desktop / Copilot)
2. The first time, say **"Login to FLEX"** ,Chrome will open for CAPTCHA
3. If image CAPTCHA appears, solve it manually (you have 2 minutes)
4. Once logged in, ask away!

## Available Tools

| Tool | Description |
|------|-------------|
| `login` | Opens Chrome for CAPTCHA-authenticated login |
| `get_attendance` | Fetches attendance for all courses |
| `get_marks` | Gets detailed marks with class statistics |
| `get_transcript` | Full academic transcript with GPAs |
| `get_mca` | Modified Class Average for relative grading |
| `get_courses` | Current semester registered courses |
| `get_fee_report` | Payment history and fee details |
| `check_login_status` | Verify if session is active |

## Project Structure

```
FLEX/
├── server.py           # MCP entry point
├── auth.py             # Login & session management
├── tools/              # MCP tool implementations
│   ├── login.py
│   ├── attendance.py
│   ├── marks.py
│   ├── transcript.py
│   ├── mca.py
│   ├── courses.py
│   ├── fees.py
│   └── status.py
└── parsers/            # HTML parsing logic
    ├── attendance.py
    ├── marks.py
    ├── transcript.py
    ├── courses.py
    ├── fees.py
    └── challan.py
```

## Notes

- Login session persists until you restart the MCP server
- Chrome must be installed (Other browsers are not supported, well if you can add support please do)
- Your credentials are only used locally, never transmitted elsewhere
- Image CAPTCHAs require manual solving, the browser stays open for you
