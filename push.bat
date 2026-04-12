@echo off
echo Pushing to GitHub...
cd /d "d:\AI CONTENT INTELLIGENCE SYSTEM"
git add -A
git commit -m "Update: %date% %time%"
git push origin main
echo Done!
pause
