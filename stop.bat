@echo off
REM Windows Batch wrapper for stop.ps1

powershell.exe -ExecutionPolicy Bypass -File "%~dp0stop.ps1"
