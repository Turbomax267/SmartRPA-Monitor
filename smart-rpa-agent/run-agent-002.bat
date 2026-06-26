@echo off
cd /d "%~dp0"
set SMART_RPA_API_URL=https://smartrpa-monitor-backend.onrender.com/api
set SMART_RPA_AGENT_TOKEN=agent-002-token
set AGENT_NAME=AGENT-002
set SMART_RPA_TIMEOUT=30
set SMART_RPA_POLL_INTERVAL=5
".\.venv\Scripts\python.exe" main.py worker
