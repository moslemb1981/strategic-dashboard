@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat

python setup.py build_ext --inplace

echo.
echo Cleaning up .c files...
del /Q strategic\*.c

echo.
echo Done.
pause