# Quick Start Script for Docker
# Run this script to start the project with Docker

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Big Data Sentiment Analysis - Docker Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Starting Docker containers..." -ForegroundColor Yellow
docker-compose up --build -d

Write-Host ""
Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Services are starting!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access the following URLs:" -ForegroundColor Cyan
Write-Host "  - Django Dashboard: http://localhost:8000" -ForegroundColor White
Write-Host "  - Classify Text: http://localhost:8000/classify" -ForegroundColor White
Write-Host "  - Grafana: http://localhost:3000 (admin/admin)" -ForegroundColor White
Write-Host "  - Prometheus: http://localhost:9090" -ForegroundColor White
Write-Host ""
Write-Host "To view logs, run:" -ForegroundColor Yellow
Write-Host "  docker-compose logs -f" -ForegroundColor White
Write-Host ""
Write-Host "To stop all services, run:" -ForegroundColor Yellow
Write-Host "  docker-compose down" -ForegroundColor White
Write-Host ""
