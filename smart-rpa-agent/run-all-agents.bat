@echo off
cd /d "%~dp0"
start "AGENT-001" cmd /k "%~dp0run-agent-001.bat"
start "AGENT-002" cmd /k "%~dp0run-agent-002.bat"
start "AGENT-003" cmd /k "%~dp0run-agent-003.bat"
start "AGENT-004" cmd /k "%~dp0run-agent-004.bat"
start "AGENT-005" cmd /k "%~dp0run-agent-005.bat"
