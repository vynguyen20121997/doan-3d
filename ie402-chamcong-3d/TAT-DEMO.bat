@echo off
REM  Tat may chu Node va PostgreSQL sau khi demo xong.
chcp 65001 >nul
title Cham cong 3D - dang tat...

echo [1/2] Tat may chu Node (cong 3000)...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":3000" ^| findstr "LISTENING"') do taskkill /PID %%p /F >nul 2>&1

echo [2/2] Tat PostgreSQL...
"D:\pgportable\pgsql\bin\pg_ctl.exe" -D D:\pgportable\data stop

echo.
echo Da tat xong.
ping -n 5 127.0.0.1 >nul
