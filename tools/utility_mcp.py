#!/usr/bin/env python3
"""
MCP Server: Utility
General helper tools for AIS.
"""

import os, sys, subprocess
from typing import Dict, Any

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    from fastmcp import FastMCP

mcp = FastMCP("Utility")

@mcp.tool()
def copy_to_clipboard(text: str) -> Dict[str, Any]:
    """
    Copies the provided text to the system clipboard.
    Useful for triggering VoxClip.
    """
    try:
        # Use PowerShell to set clipboard (cross-platform alternative to pyperclip for simple CLI usage)
        process = subprocess.Popen(['powershell.exe', '-NoProfile', '-Command', 'Set-Clipboard -Value $Input'], stdin=subprocess.PIPE)
        process.communicate(input=text.encode('utf-16'))
        return {"ok": True, "message": "Text copied to clipboard."}
    except Exception as e:
        return {"ok": False, "error": str(e)}

if __name__ == "__main__":
    mcp.run()
