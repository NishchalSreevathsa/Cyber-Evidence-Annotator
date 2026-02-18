# 🛡️ Cyber Evidence Annotator (MCP Agent)
 
*Building Autonomous Agents with the Model Context Protocol (MCP)*

## 📖 Overview
The **Cyber Evidence Annotator** is an Agentic AI application that demonstrates how Large Language Models (LLMs) can step out of the browser to control local Desktop Applications and external APIs. 

Built using the **Model Context Protocol (MCP)**, this tool allows a Security Analyst to use natural language to:
1.  **Launch** local desktop tools (MS Paint) to view evidence.
2.  **Analyze & Mark** evidence with classification stamps (e.g., "CONFIDENTIAL").
3.  **Isolate Threats** by manipulating the application window.
4.  **Report** findings via Email (Gmail API Integration).

---

## 🚩 The Problem: SOC Analyst Burnout
In a modern Security Operations Center (SOC), analysts spend 40% of their time on repetitive, manual tasks:
*   Taking screenshots of malware analysis.
*   Manually opening image editors to crop/highlight evidence.
*   Drafting boilerplate emails to the CISO or Incident Response team.

This context-switching leads to **Alert Fatigue** and burnout, increasing the risk of missing genuine threats.

## 💡 The Solution: Agentic Automation
We replace this manual workflow with an **AI Agent** that can "use" the computer like a human. 

By implementing **MCP (Model Context Protocol)**, we standardize how the AI connects to tools. The AI doesn't just "generate text"—it generates **Actions** that are executed on the host OS.

---

## 🏗️ Technical Architecture

This project is built on three core pillars:

### 1. MCP Server (`mcp_server.py`)
*   **Role:** The "Hands" of the Agent.
*   **Technology:** Python, `mcp` SDK, `pywinauto`.
*   **Function:** Exposes tools to the AI:
    *   `open_evidence_locker`: Launches `mspaint.exe` with a specific evidence file.
    *   `stamp_classification`: Types text into the active window.
    *   `draw_threat_border`: Manipulates the window state (Maximize/Restore) to signal alert.
    *   `send_gmail_alert`: Simulates sending an urgent email via Gmail API.

### 2. MCP Client (`talk2mcp.py`)
*   **Role:** The "Ears" and "Brain" of the Agent.
*   **Technology:** FastAPI, Uvicorn, Jinja2.
*   **Function:**
    *   Hosts a Cyber-themed Web UI (`http://localhost:8001`).
    *   Accepts user commands ("Open the locker").
    *   **Simulation Mode:** Uses robust keyword matching for instant, offline execution.
    *   **LLM Mode:** Uses **Google Gemini API** to reason and plan complex workflows.

### 3. Key Concepts Applied 
*   **Asyncio:** Used throughout the server to handle concurrent tool calls without blocking the UI. Like a Chef managing multiple pots on a stove.
*   **Decorators:** Used to register tools (`@server.call_tool()`), acting like a "VIP List" or Web Application Firewall (WAF) that wraps the function with extra logic.
*   **Dotenv:** Securely managing configuration and API keys (The "Vault").

---

## 🚀 Installation & Usage

### Prerequisites
*   Python 3.10 or higher.
*   Windows OS (Required for `pywinauto` to control MS Paint).

### Setup
1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/NishchalSreevathsa/session-4-mcp-agent.git
    cd session-4-mcp-agent
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r Assignment/requirements.txt
    ```

3.  **Run the Application:**
    ```bash
    cd Assignment
    python talk2mcp.py
    ```

4.  **Access the Dashboard:**
    Open your browser to `http://localhost:8001`.

---

## 🧪 Test Cases

### Scenario 1: Simulation Mode (No API Key)
*Ideal for testing speed and tool connectivity.*

| Command | Action | Expected Output |
| :--- | :--- | :--- |
| **Click [LAUNCH EVIDENCE]** | Launches Paint | MS Paint opens with `evidence.png` loaded. |
| **Click [STAMP: CONFIDENTIAL]** | Stamps Text | Logs: `Stamped 'CONFIDENTIAL' on the evidence.` |
| **Click [DRAW BORDER]** | Highlights Window | Paint window Flashes (Maximize/Restore). |
| **Type "Send email to CISO"** | Sends Alert | Logs: `Email sent to ciso@cybercorp.com...` |

### Scenario 2: AI Agent Mode (With API Key)
*Demonstrates Reasoning and Intent Understanding.*

1.  Enter your **Google Gemini API Key** in the top input box.
2.  Type a complex command: *"Open the locker and mark it as confidential, then alert the boss."*
3.  **Result:** The LLM interprets this and calls the tools in sequence:
    *   `open_evidence_locker()`
    *   `stamp_classification('CONFIDENTIAL')`
    *   `send_gmail_alert(...)`

---

## 🏁 Conclusion
This project demonstrates that **Agents are the new Apps**. By standardizing tool interfaces with MCP, we can build modular, secure, and powerful automation systems that bridge the gap between AI reasoning and real-world action.

---
*Created by Nishchal Sreevathsa*
