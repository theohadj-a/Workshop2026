@echo off
REM Script lanceur de build automatique pour PROJECT RESILIENCE-ALPHA
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\build-images.ps1" %*
