@echo off
title BAM Sucks - raw recovered crawl (localhost:8081)
cd /d "%~dp0recovered_site"
echo.
echo ================================================
echo  BAM Sucks - RAW RECOVERED CRAWL (comparison)
echo ================================================
echo.
echo This is the "recovered_site" raw crawl folder.
echo Use this to compare against the editable source.
echo.
echo Open in your browser:
echo   http://localhost:8081
echo.
echo The server is now running in this window.
echo Press Ctrl+C to stop, then close the window.
echo.
"C:\Users\danie\AppData\Local\Programs\Python\Python314\python.exe" -m http.server 8081 --bind 127.0.0.1
echo.
echo Server stopped.
pause >nul
