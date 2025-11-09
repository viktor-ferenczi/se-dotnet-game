@echo off

if exist .git goto skip1
echo Preparing local Git repository...
git init
if %ERRORLEVEL% NEQ 0 goto failed
git add .gitignore
if %ERRORLEVEL% NEQ 0 goto failed
git commit -m "Git ignore"
if %ERRORLEVEL% NEQ 0 goto failed
git add .
if %ERRORLEVEL% NEQ 0 goto failed
git commit -m "Initial"
if %ERRORLEVEL% NEQ 0 goto failed
echo ==========
:skip1

if exist Bin64 goto skip2
call LinkBin64.bat
if %ERRORLEVEL% NEQ 0 goto failed
echo ==========
:skip2


if exist VRage.XmlSerializers goto skip3
echo Decompiling the game... (10-20 minutes)
call Decompile.bat
if %ERRORLEVEL% NEQ 0 goto failed
echo Committing the code into the local Git repository...
git add .
if %ERRORLEVEL% NEQ 0 goto failed
git commit -m "Decompiled code"
if %ERRORLEVEL% NEQ 0 goto failed
echo ==========
:skip3


if exist FixBulk_applied.txt goto skip4
echo Applying bulk fixes
python -OO -u FixBulk.py
if %ERRORLEVEL% NEQ 0 goto failed
echo OK >FixBulk_applied.txt
git add .
if %ERRORLEVEL% NEQ 0 goto failed
git commit -m "Bulk fixes"
if %ERRORLEVEL% NEQ 0 goto failed
echo ==========
:skip4


if exist VRage\ReplicatedTypes.json goto skip5
echo Copying replicated type info
copy ReplicatedTypes.json VRage\
if %ERRORLEVEL% NEQ 0 goto failed
git add .
if %ERRORLEVEL% NEQ 0 goto failed
git commit -m "Replicated types"
if %ERRORLEVEL% NEQ 0 goto failed
echo ==========
:skip5


if exist Manual_fixes_applied.txt goto skip6
echo Applying manual fixes (whitespace warnings are normal)
git apply --ignore-whitespace Manual_fixes.patch
if %ERRORLEVEL% NEQ 0 goto failed
echo OK >Manual_fixes_applied.txt
git add .
if %ERRORLEVEL% NEQ 0 goto failed
git commit -m "Manual fixes"
if %ERRORLEVEL% NEQ 0 goto failed
echo ==========
:skip6


echo Restoring NuGet packages
dotnet restore --force
if %ERRORLEVEL% NEQ 0 goto failed
echo ==========

echo DONE
exit /b 0

:failed
echo FAILED
exit /b 1
