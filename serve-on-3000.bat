@echo off
title BAM Sucks - LOCALHOST:3000 (full current source)
cd /d "%~dp0"
echo.
echo ===============================================
echo  BAM Sucks - LOCAL TEST SERVER (root)
echo ===============================================
echo.
echo Open this in your browser:
echo   http://localhost:3000
echo.
echo IMPORTANT:
echo - Use the URL above (localhost), NOT bamsucks.com
echo - Do NOT double-click index.html directly (use the server)
echo - Click "Read page" links to test individual document pages (now should resolve)
echo - /topics/ links should also work
echo - The address bar must show localhost:3000 for local testing
echo.
echo Close this window or press Ctrl+C to stop the server.
echo.
python -m http.server 3000 --bind 127.0.0.1
echo.
echo Server stopped.
pause >nul
