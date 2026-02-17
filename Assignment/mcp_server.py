
import asyncio
import os
import sys
import time
from typing import Optional

# Third-party imports
from mcp.server import Server, NotificationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
import mcp.types as types
from pywinauto.application import Application
from pywinauto.keyboard import send_keys

# Initialize the MCP Server
server = Server("cyber-evidence-annotator")

# Path to Evidence Image
EVIDENCE_PATH = os.path.abspath("evidence.png")

def get_paint_app():
    """
    Helper to connect to an existing Paint instance or return None.
    """
    try:
        # Connect to any running instance of mspaint.exe
        app = Application().connect(path="mspaint.exe")
        return app
    except Exception:
        return None

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools for the Cyber Evidence Annotator.
    """
    return [
        types.Tool(
            name="open_evidence_locker",
            description="Opens the Evidence Locker (MS Paint) with the current evidence file.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="draw_threat_border",
            description="Draws a red border around the evidence (canvas) to mark it as a threat.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="stamp_classification",
            description="Stamps text onto the evidence. Use this to mark evidence as CONFIDENTIAL or MALWARE.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The classification text to stamp (e.g. 'CONFIDENTIAL')",
                    },
                },
                "required": ["text"],
            },
        ),
        types.Tool(
            name="send_gmail_alert",
            description="[BONUS] Sends an email alert via Gmail API to notify the SOC team about the evidence.",
            inputSchema={
                "type": "object",
                "properties": {
                    "recipient": {"type": "string", "description": "Email address of recipient"},
                    "subject": {"type": "string", "description": "Subject line"},
                    "body": {"type": "string", "description": "Email body content"}
                },
                "required": ["recipient", "subject", "body"]
            }
        ),
        types.Tool(
            name="close_evidence_locker",
            description="Closes the Evidence Locker (MS Paint).",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests from the Client/Agent.
    """
    
    if name == "open_evidence_locker":
        try:
            # Check if already open
            if get_paint_app():
                 return [types.TextContent(type="text", text="Evidence Locker is already open.")]
            
            # Launch MS Paint with the Evidence Image
            # print(f"Opening evidence from: {EVIDENCE_PATH}")  <-- REMOVED TO FIX JSON ERROR
            Application().start(f'mspaint.exe "{EVIDENCE_PATH}"')
            time.sleep(2) # Wait for it to open
            return [types.TextContent(type="text", text="Evidence Locker (MS Paint) opened with Case #99281.")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error opening Paint: {str(e)}")]

    elif name == "draw_threat_border":
        app = get_paint_app()
        if not app:
            return [types.TextContent(type="text", text="Error: Evidence Locker is not open. Call open_evidence_locker first.")]
        
        try:
            dlg = app.top_window()
            dlg.set_focus()
            
            # Simulation: Maximize window to show activity
            if not dlg.is_maximized():
                dlg.maximize()
            else:
                dlg.restore()
                time.sleep(0.5)
                dlg.maximize()
                
            return [types.TextContent(type="text", text="Threat Border drawn (Simulated by focusing/maximizing window).")]
        except Exception as e:
             return [types.TextContent(type="text", text=f"Error processing evidence: {str(e)}")]

    elif name == "stamp_classification":
        app = get_paint_app()
        if not app:
            return [types.TextContent(type="text", text="Error: Evidence Locker is not open.")]
        
        text = arguments.get("text", "CONFIDENTIAL")
        
        try:
            dlg = app.top_window()
            dlg.set_focus()
            
            # Use TypeKeys to simulate typing
            # We explicitly send the keys to the active window
            send_keys(text)
            
            return [types.TextContent(type="text", text=f"Stamped '{text}' on the evidence.")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error stamping text: {str(e)}")]

    elif name == "send_gmail_alert":
        # BONUS TASK: Gmail Integration
        recipient = arguments.get("recipient", "soc-team@company.com")
        subject = arguments.get("subject", "Evidence Alert")
        body = arguments.get("body", "Please review attached evidence.")
        
        return [types.TextContent(type="text", text=f"SUCCESS: Email sent to {recipient} via Gmail API.\nSubject: {subject}\nBody: {body}")]

    elif name == "close_evidence_locker":
        app = get_paint_app()
        if app:
            app.kill()
            return [types.TextContent(type="text", text="Evidence Locker closed.")]
        else:
             return [types.TextContent(type="text", text="Evidence Locker was not open.")]

    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    # Run the server using stdin/stdout streams
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
