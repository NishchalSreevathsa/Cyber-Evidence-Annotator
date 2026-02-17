
import asyncio
import os
import sys
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List

# MCP Imports
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession
from mcp.types import CallToolRequestParams, CallToolResult

# LLM Imports
import google.generativeai as genai

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Configuration
SERVER_SCRIPT = os.path.join(os.path.dirname(__file__), "mcp_server.py")

class ChatRequest(BaseModel):
    prompt: str
    api_key: Optional[str] = None

class StepLog(BaseModel):
    tool: str
    result: str

class ChatResponse(BaseModel):
    status: str
    message: str
    steps: List[StepLog] = []
    detail: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

async def run_mcp_interaction(prompt: str, api_key: str | None) -> ChatResponse:
    """
    Connects to the MCP Server, decides on a tool (Simulated or LLM), and executes it.
    """
    # Environment Setup for subprocess
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    
    steps_log = []
    final_message = "Task completed."

    # Establish connection to MCP Server
    # We use 'python mcp_server.py' as the command
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[SERVER_SCRIPT],
        env=env
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # List Available Tools
                tools_response = await session.list_tools()
                available_tools = {t.name: t for t in tools_response.tools}
                
                # DECISION LOGIC
                tool_to_call = None
                tool_args = {}

                # 1. SIMULATION MODE (Robust fallback)
                prompt_lower = prompt.lower()
                
                if "launch" in prompt_lower or "open" in prompt_lower:
                    tool_to_call = "open_evidence_locker"
                    
                # Fix: Check for specific "stamp/confidential" commands BEFORE generic "mark" commands
                elif "stamp" in prompt_lower or "classify" in prompt_lower or "confidential" in prompt_lower:
                    tool_to_call = "stamp_classification"
                    tool_args = {"text": "CONFIDENTIAL"}

                elif "box" in prompt_lower or "border" in prompt_lower or "mark" in prompt_lower:
                    tool_to_call = "draw_threat_border"
                    
                elif "email" in prompt_lower or "gmail" in prompt_lower or "send" in prompt_lower:
                    tool_to_call = "send_gmail_alert"
                    tool_args = {
                        "recipient": "ciso@cybercorp.com", 
                        "subject": "Evidence Alert - Session 4", 
                        "body": "Evidence has been marked as CONFIDENTIAL."
                    }
                    
                elif "close" in prompt_lower:
                    tool_to_call = "close_evidence_locker"

                # 2. LLM MODE (If API Key is present)
                if api_key:
                    try:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel('gemini-pro')
                        
                        tool_desc = "\n".join([f"- {t.name}: {t.description}" for t in available_tools.values()])
                        llm_prompt = f"""
                        You are an Agent controlling a Paint application and Email.
                        Available Tools:
                        {tool_desc}
                        
                        User Request: "{prompt}"
                        
                        Return ONLY a JSON object with the tool name and arguments. 
                        Example: {{"tool": "open_evidence_locker", "args": {{}}}}
                        """
                        response = model.generate_content(llm_prompt)
                        # Parse JSON from response (Simplified)
                        import json
                        import re
                        match = re.search(r"\{.*\}", response.text, re.DOTALL)
                        if match:
                            json_str = match.group(0)
                            plan = json.loads(json_str)
                            tool_to_call = plan.get("tool")
                            tool_args = plan.get("args", {})
                            final_message = f"AI decided to call {tool_to_call}"
                    except Exception as e:
                        print(f"LLM Error: {e}. Falling back to simulation.")

                # EXECUTION
                if tool_to_call and tool_to_call in available_tools:
                    result = await session.call_tool(tool_to_call, arguments=tool_args)
                    
                    # Process result
                    text_res = "Success"
                    if result.content and len(result.content) > 0:
                        text_res = result.content[0].text
                    
                    steps_log.append(StepLog(tool=tool_to_call, result=text_res))
                    if not api_key:
                        final_message = f"Execute command '{prompt}': Called {tool_to_call}."
                else:
                    final_message = "I didn't understand that command or no matching tool found."
                    if not api_key:
                        final_message += " (Simulation Mode: Try 'launch', 'draw box', 'stamp text', 'send email')"

    except Exception as e:
        return ChatResponse(status="error", message="Failed", detail=str(e))

    return ChatResponse(status="success", message=final_message, steps=steps_log)

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    return await run_mcp_interaction(request.prompt, request.api_key)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
