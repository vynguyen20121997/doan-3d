@echo off
REM ============================================================
REM  CAI DAT LAN DAU — chay MOT LAN sau khi clone repo ve.
REM    1. Cai thu vien Node (npm install)
REM    2. Tao co so du lieu chamcong3d + bat extension PostGIS
REM    3. Nap schema.sql va seed.sql
REM  Sau buoc nay, moi lan demo chi can chay BAT-DEMO.bat.
REM ============================================================
setlocal enabledelayedexpansion
chcp 65001 >nul
title Cham cong 3D - cai dat lan dau

set "DUAN=%~dp0"
cd /d "%DUAN%"

echo.
echo ============================================================
echo  CAI DAT HE THONG CHAM CONG DINH VI 3D
echo ============================================================

REM ---------- 0. Kiem tra Node ----------
echo.
echo [0/4] Kiem tra Node.js...
where node >nul 2>&1
if errorlevel 1 (
  echo.
  echo  *** KHONG TIM THAY Node.js ***
  echo  Tai ban LTS tai https://nodejs.org roi cai, sau do chay lai tep nay.
  pause
  exit /b 1
)
for /f "delims=" %%V in ('node -v') do echo       Node %%V - OK

REM ---------- 1. Tim PostgreSQL ----------
echo.
echo [1/4] Tim PostgreSQL + PostGIS...
call "%DUAN%TIM-POSTGRES.bat"
if errorlevel 1 (
  echo.
  echo  *** KHONG TIM THAY PostgreSQL ***
  echo.
  echo  He thong can PostgreSQL 16+ CO extension PostGIS.
  echo  Cach don gian nhat la dung ban portable, xem huong dan day du o:
  echo      %DUAN%db\README.md
  echo.
  echo  Neu da cai o cho khac, dat bien moi truong PGBIN roi chay lai:
  echo      set PGBIN=D:\duong\dan\pgsql\bin
  pause
  exit /b 1
)
echo       Tim thay: %PGBIN%

REM ---------- 2. npm install ----------
echo.
echo [2/4] Cai thu vien Node (co the mat 1-2 phut)...
pushd "%DUAN%server"
call npm install
if errorlevel 1 (
  echo  *** npm install that bai ***
  popd
  pause
  exit /b 1
)
popd
echo       Xong.

REM ---------- 3. Bat PostgreSQL neu chua chay ----------
echo.
echo [3/4] Bat PostgreSQL va tao co so du lieu...
"%PGBIN%\pg_isready.exe" -h 127.0.0.1 -p 55432 >nul 2>&1
if errorlevel 1 (
  if exist "D:\pgportable\data" (
    "%PGBIN%\pg_ctl.exe" -D D:\pgportable\data -o "-p 55432 -c listen_addresses=127.0.0.1" -l D:\pgportable\server.log start
    ping -n 7 127.0.0.1 >nul
  ) else (
    echo  *** PostgreSQL chua chay va khong thay thu muc du lieu D:\pgportable\data ***
    echo  Xem db\README.md de dung CSDL lan dau.
    pause
    exit /b 1
  )
)

"%PGBIN%\createdb.exe" -h 127.0.0.1 -p 55432 -U postgres chamcong3d 2>nul
if errorlevel 1 (
  echo       CSDL chamcong3d da co san - se nap de len.
) else (
  echo       Da tao CSDL chamcong3d.
)

"%PGBIN%\psql.exe" -h 127.0.0.1 -p 55432 -U postgres -d chamcong3d -c "CREATE EXTENSION IF NOT EXISTS postgis;" >nul
if errorlevel 1 (
  echo.
  echo  *** KHONG BAT DUOC EXTENSION PostGIS ***
  echo  Ban PostgreSQL nay chua cai PostGIS. Xem db\README.md.
  pause
  exit /b 1
)
echo       PostGIS - OK

REM ---------- 4. Nap schema + seed ----------
echo.
echo [4/4] Nap schema.sql va seed.sql...
"%PGBIN%\psql.exe" -h 127.0.0.1 -p 55432 -U postgres -d chamcong3d -v ON_ERROR_STOP=1 -q -f "%DUAN%db\schema.sql"
if errorlevel 1 ( echo  *** schema.sql loi *** & pause & exit /b 1 )
"%PGBIN%\psql.exe" -h 127.0.0.1 -p 55432 -U postgres -d chamcong3d -v ON_ERROR_STOP=1 -q -f "%DUAN%db\seed.sql"
if errorlevel 1 ( echo  *** seed.sql loi *** & pause & exit /b 1 )

echo.
"%PGBIN%\psql.exe" -h 127.0.0.1 -p 55432 -U postgres -d chamcong3d -c "SELECT count(*) AS so_nhan_vien FROM nhan_vien;"

echo.
echo ============================================================
echo  CAI DAT XONG.
echo  Tu gio moi lan demo chi can nhay dup: BAT-DEMO.bat
echo ============================================================
pause
