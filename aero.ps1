param (
    [string]$Action
)

if ($Action -eq "onboard") {
    python scripts\onboard.py
} else {
    Write-Host ""
    Write-Host "🚀 AI-Aero CLI" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "  aero onboard    - Launch the agent configuration tool"
    Write-Host ""
}
