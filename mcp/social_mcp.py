#!/usr/bin/env python3
"""
MCP Server: Social Automation
Tools for TikTok and Pinterest automation.
"""

import os, sys, logging
from pathlib import Path
from typing import Optional, Dict, Any

# Add tools directory to path
sys.path.append(str(Path(__file__).parent / "tools"))

from social_automation import SocialAutomation

# ----- FastMCP -----
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    from fastmcp import FastMCP  # type: ignore

mcp = FastMCP("Social Automation")

# Global instance
_AUTO = SocialAutomation()

@mcp.tool()
def tiktok_login(email: str, password: str) -> Dict[str, Any]:
    """
    Login to TikTok using stealth browser.
    """
    ok = _AUTO.tiktok_login(email, password)
    return {"ok": ok, "message": "Login successful" if ok else "Login failed"}

@mcp.tool()
def tiktok_post_video(video_path: str, caption: str) -> Dict[str, Any]:
    """
    Post a video to TikTok.
    """
    ok = _AUTO.tiktok_post_video(video_path, caption)
    return {"ok": ok, "message": "Video posted" if ok else "Post failed"}

@mcp.tool()
def tiktok_upload_profile_pic(image_path: str) -> Dict[str, Any]:
    """
    Upload a profile picture to TikTok.
    """
    ok = _AUTO.tiktok_upload_profile_pic(image_path)
    return {"ok": ok, "message": "Photo uploaded" if ok else "Upload failed"}

@mcp.tool()
def pinterest_login(email: str, password: str) -> Dict[str, Any]:
    """
    Login to Pinterest.
    """
    ok = _AUTO.pinterest_login(email, password)
    return {"ok": ok, "message": "Login successful" if ok else "Login failed"}

@mcp.tool()
def pinterest_create_pin(
    image_path: str, 
    title: str, 
    description: str, 
    link: str, 
    board: str = "Wrist Care"
) -> Dict[str, Any]:
    """
    Create a pin on Pinterest.
    """
    ok = _AUTO.pinterest_create_pin(image_path, title, description, link, board)
    return {"ok": ok, "message": "Pin created" if ok else "Pin creation failed"}

if __name__ == "__main__":
    mcp.run()
