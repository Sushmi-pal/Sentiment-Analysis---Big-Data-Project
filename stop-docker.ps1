# Stop Docker Script
# Run this to stop all containers

Write-Host "========================================" -ForegroundColor Red
Write-Host "Stopping Docker Containers" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""

docker-compose down

Write-Host ""
Write-Host "✅ All containers stopped!" -ForegroundColor Green
Write-Host ""
Write-Host "To remove all data (including database), run:" -ForegroundColor Yellow
Write-Host "  docker-compose down -v" -ForegroundColor White
Write-Host ""
