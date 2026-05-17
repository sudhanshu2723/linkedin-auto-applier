# setup_scheduler.ps1
# Run this ONCE to register the daily Task Scheduler job
# Usage: powershell -ExecutionPolicy Bypass -File setup_scheduler.ps1
# No admin required - registers as current user task

$TaskName  = "LinkedInAutoJobApplier"
$BotDir    = "D:\Github_Codes\Job_Search\Auto_job_applier_linkedIn"
$BatFile   = "$BotDir\run_bot.bat"
$LogFile   = "$BotDir\logs\scheduler.log"

# ── What time to run daily ──────────────────────────────────────────────────
# Change this to your preferred start time (24-hour format HH:MM)
$StartTime = "09:00"

Write-Host "Setting up LinkedIn Auto Job Applier daily scheduler..." -ForegroundColor Cyan
Write-Host "Bot directory : $BotDir"
Write-Host "Runs daily at : $StartTime"
Write-Host ""

# Remove existing task if it exists
schtasks /delete /tn $TaskName /f 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Removed existing task." -ForegroundColor Yellow
}

# Register using schtasks (no admin needed for current user)
$result = schtasks /create `
    /tn $TaskName `
    /tr "`"$BatFile`"" `
    /sc DAILY `
    /st $StartTime `
    /f 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "Task registered successfully!" -ForegroundColor Green
} else {
    Write-Host "Failed to register task: $result" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Scheduled task info:" -ForegroundColor Cyan
schtasks /query /tn $TaskName /fo LIST

Write-Host ""
Write-Host "To manage the task:" -ForegroundColor Yellow
Write-Host "  Run now : schtasks /run /tn $TaskName"
Write-Host "  Remove  : schtasks /delete /tn $TaskName /f"
Write-Host "  View    : schtasks /query /tn $TaskName /fo LIST"
Write-Host "  Logs    : Get-Content '$LogFile' -Tail 50"
Write-Host ""
Write-Host "Or open Task Scheduler GUI: taskschd.msc"
