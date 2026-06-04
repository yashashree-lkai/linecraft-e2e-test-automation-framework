@echo off
echo ============================================
echo  Linecraft AI - Playwright Regression Suite
echo  %date% %time%
echo ============================================

cd C:\Users\y80150038\Downloads\playwright_framework\playwright_framework

call .venv\Scripts\activate

echo Running regression tests...
pytest tests\ --base-url=http://wks1103/signin -v -s --html=reports\regression_%date:~-4,4%%date:~-10,2%%date:~-7,2%.html --self-contained-html

echo.
echo Done! Report saved to reports folder.
echo ============================================
pause