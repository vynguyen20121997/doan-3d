@echo off
REM ------------------------------------------------------------
REM  Tim thu muc bin cua PostgreSQL, dat vao bien PGBIN.
REM  Duoc goi boi CAI-DAT.bat va BAT-DEMO.bat — khong chay rieng.
REM  Thu tu uu tien: bien moi truong PGBIN -> cac duong dan quen
REM  thuoc -> psql.exe co san trong PATH.
REM ------------------------------------------------------------
if defined PGBIN if exist "%PGBIN%\psql.exe" exit /b 0

for %%D in (
  "D:\pgportable\pgsql\bin"
  "C:\pgportable\pgsql\bin"
  "%USERPROFILE%\pgportable\pgsql\bin"
  "C:\Program Files\PostgreSQL\17\bin"
  "C:\Program Files\PostgreSQL\16\bin"
) do (
  if exist "%%~D\psql.exe" (
    set "PGBIN=%%~D"
    exit /b 0
  )
)

for /f "delims=" %%P in ('where psql 2^>nul') do (
  set "PGBIN=%%~dpP"
  exit /b 0
)

exit /b 1
