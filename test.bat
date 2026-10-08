@echo off
rem ===========================================================================
rem  Shelfcall - every check, in the order they fail fastest.
rem  Double-click, or run from a terminal in this folder.
rem  Needs: Node (any recent), Python 3, and once:
rem      py -m pip install playwright
rem      py -m playwright install chromium
rem ===========================================================================
cd /d "%~dp0"
set "PY=py -3"
where py >nul 2>nul || set "PY=python"

echo.
echo  1/4  Build the pages
%PY% build\build.py || goto :fail

echo.
echo  2/4  Unit tests (merge rules, server)
node --test tests\sync-core.test.js tests\world-api.test.js || goto :fail

echo.
echo  3/4  End-to-end flows across roles
%PY% tests\e2e\flows.py || goto :fail

echo.
echo  4/4  Contrast, light and dark
%PY% tests\tools\contrast.py || goto :fail

echo.
echo  All checks passed.
pause
exit /b 0

:fail
echo.
echo  A check failed - see above.
pause
exit /b 1
