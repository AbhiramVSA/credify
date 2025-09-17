# Reset database script for Windows
Write-Host "Resetting database for UUID conversion..." -ForegroundColor Green

# Stop any running containers
Write-Host "Stopping containers..." -ForegroundColor Yellow
docker-compose down

# Remove the database volume to start fresh
Write-Host "Removing database volume..." -ForegroundColor Yellow
docker volume rm alemno-backend_postgres_data 2>$null

# Remove migration files (keep __init__.py)
Write-Host "Cleaning migration files..." -ForegroundColor Yellow
Get-ChildItem "src\core\migrations\*.py" | Where-Object { $_.Name -ne "__init__.py" } | Remove-Item -Force

# Start containers
Write-Host "Starting fresh containers..." -ForegroundColor Green
docker-compose up --build