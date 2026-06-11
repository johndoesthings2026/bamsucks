@echo off
title BAM Sucks - current editable source (localhost:8080)
cd /d "%~dp0current-site-source"
echo.
echo ================================================
echo  BAM Sucks - RECOVERED CURRENT EDITABLE SOURCE
echo ================================================
echo.
echo This is the "current editable static source" folder.
echo (The one the README calls the editable version.)
echo.
echo Open in your browser:
echo   http://localhost:8080
echo.
echo The server is now running in this window.
echo Access logs will appear here.
echo Press Ctrl+C to stop, then close the window.
echo.
"C:\Users\danie\AppData\Local\Programs\Python\Python314\python.exe" -m http.server 8080 --bind 127.0.0.1
echo.
echo Server stopped.
pause >nul
