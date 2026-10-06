@echo off
title SENTIMENTIQ - AI Text Sentiment Intelligence
if exist %~dp0app.py (
    cd /d %~dp0
) else (
    cd /d %~dp0sentimentiq
)
echo ===================================================
echo   SENTIMENTIQ - AI-Powered Text Sentiment Intelligence
echo   Project 2 | QSkill Python Development Internship
echo ===================================================
echo Starting application server at http://127.0.0.1:5000 ...
start http://127.0.0.1:5000
python app.py
pause
