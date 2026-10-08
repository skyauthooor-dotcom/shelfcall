@echo off
setlocal EnableDelayedExpansion
rem ===========================================================================
rem  Shelfcall - rebuild the site and push everything to GitHub.
rem
rem  Double-click this file. Nothing to type except, the first time only,
rem  your name and email for git and the GitHub sign-in window.
rem  Safe to run again after every change: it rebuilds public\, commits
rem  whatever changed and pushes. Vercel redeploys on each push.
rem ===========================================================================

set "REPO=https://github.com/skyauthooor-dotcom/shelfcall.git"
set "BRANCH=main"

cd /d "%~dp0"
echo.
echo  Shelfcall - push to %REPO%
echo  -------------------------------------------------------------------

rem ---- git must be installed ------------------------------------------------
where git >nul 2>nul
if errorlevel 1 (
  echo  Git is not installed. Get it from https://git-scm.com/download/win
  echo  then run this again.
  goto :fail
)

rem ---- rebuild public\ from the master, if Python is here -------------------
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY ( where python >nul 2>nul && set "PY=python" )
if defined PY (
  echo  Rebuilding public\ ...
  %PY% build\build.py
  if errorlevel 1 (
    echo  The build failed - nothing was pushed. Read the message above.
    goto :fail
  )
) else (
  echo  Python not found - pushing public\ as it is, without rebuilding.
)

rem ---- a repository with the GitHub remote ----------------------------------
if not exist ".git" (
  echo  Creating the git repository ...
  git init -q
  git symbolic-ref HEAD refs/heads/%BRANCH%
)

git remote get-url origin >nul 2>nul
if errorlevel 1 (
  git remote add origin %REPO%
) else (
  git remote set-url origin %REPO%
)

rem ---- git needs a name and email to commit ---------------------------------
git config user.name >nul 2>nul
if errorlevel 1 (
  set /p "GNAME=  Your name for commits: "
  git config user.name "!GNAME!"
)
git config user.email >nul 2>nul
if errorlevel 1 (
  set /p "GMAIL=  Your GitHub email: "
  git config user.email "!GMAIL!"
)

rem ---- commit whatever changed ----------------------------------------------
git add -A
git diff --cached --quiet
if errorlevel 1 (
  rem  The message is written in advance in next-commit.txt, which is used
  rem  once and then removed. Without it, a plain default is used.
  if exist "next-commit.txt" (
    git commit -q -F next-commit.txt
    if errorlevel 1 ( echo  The commit failed. & goto :fail )
    del /q next-commit.txt
  ) else (
    git commit -q -m "Update Shelfcall prototype"
    if errorlevel 1 ( echo  The commit failed. & goto :fail )
  )
  echo  Committed:
  git log -1 --format="    %%s"
) else (
  echo  Nothing new to commit.
)

rem ---- push; if GitHub already has commits we don't, merge them first -------
echo  Pushing to GitHub (a sign-in window may open the first time) ...
git push -u origin %BRANCH%
if errorlevel 1 (
  echo.
  echo  GitHub has commits this folder does not. Merging them in and retrying ...
  git pull --no-rebase --no-edit --allow-unrelated-histories origin %BRANCH%
  if errorlevel 1 (
    echo  The merge stopped on a conflict. Resolve it, then run this again.
    goto :fail
  )
  git push -u origin %BRANCH%
  if errorlevel 1 goto :fail
)

echo.
echo  Done. Pushed to %REPO% on branch %BRANCH%.
echo  -------------------------------------------------------------------
pause
exit /b 0

:fail
echo.
echo  Stopped. Nothing else was changed.
pause
exit /b 1
