@echo off
title BAM Sucks - current source (full site with readers + topics) (localhost:8080)
cd /d "%~dp0"
echo.
echo ================================================
echo  BAM Sucks - current source (localhost:8080)
echo ================================================
echo.
echo Open in your browser:
echo   http://localhost:8080
echo.
echo This now includes the root catalog + all /slug/ reader pages + /topics/ hubs.
echo The server is now running in this window.
echo Access logs will appear here.
echo Press Ctrl+C to stop, then close the window.
echo.
"C:\Users\danie\AppData\Local\Programs\Python\Python314\python.exe" -m http.server 8080 --bind 127.0.0.1
echo.
echo Server stopped.
pause >nul
