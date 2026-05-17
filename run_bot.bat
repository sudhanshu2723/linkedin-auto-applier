@echo off
:: LinkedIn Auto Job Applier - Daily Runner
:: This script is called by Windows Task Scheduler every 24 hours

cd /d "D:\Github_Codes\Job_Search\Auto_job_applier_linkedIn"

:: Log the start time
echo [%date% %time%] Starting LinkedIn Auto Job Applier >> logs\scheduler.log

:: Run the bot
python runAiBot.py >> logs\scheduler.log 2>&1

:: Log the end time
echo [%date% %time%] Bot finished >> logs\scheduler.log
echo ---------------------------------------- >> logs\scheduler.log
