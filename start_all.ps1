# Start-All Services Script
# Starts Elasticsearch, Backend, and Frontend in separate windows.

$ES_PATH = "C:\Users\PC\elasticsearch\elasticsearch-9.2.4"
$BACKEND_PATH = "backend"
$FRONTEND_PATH = "frontend"

Write-Host "Starting MDP Platform Services..." -ForegroundColor Cyan

# 1. Start Elasticsearch
Write-Host "1. Starting Elasticsearch..." -ForegroundColor Yellow
if (Test-Path "$ES_PATH\bin\elasticsearch.bat") {
    Start-Process -FilePath "cmd.exe" -ArgumentList "/k cd /d $ES_PATH && bin\elasticsearch.bat" -WindowStyle Normal
    Write-Host "   Elasticsearch started." -ForegroundColor Green
} else {
    Write-Host "   Error: Elasticsearch not found at $ES_PATH" -ForegroundColor Red
}

# 2. Start Backend (using virtual environment)
Write-Host "2. Starting Backend (FastAPI)..." -ForegroundColor Yellow
$VENV_PYTHON = "$PWD\.venv\Scripts\python.exe"
if ((Test-Path $BACKEND_PATH) -and (Test-Path $VENV_PYTHON)) {
    Start-Process -FilePath "cmd.exe" -ArgumentList "/k cd /d $PWD\$BACKEND_PATH && $VENV_PYTHON -m uvicorn app.main:app --reload --port 8000" -WindowStyle Normal
    Write-Host "   Backend started on port 8000." -ForegroundColor Green
} else {
    Write-Host "   Error: Backend directory or virtual environment not found." -ForegroundColor Red
}

# 3. Start Frontend
Write-Host "3. Starting Frontend (Vite)..." -ForegroundColor Yellow
if (Test-Path $FRONTEND_PATH) {
    Start-Process -FilePath "cmd.exe" -ArgumentList "/k cd /d $PWD\$FRONTEND_PATH && npm run dev" -WindowStyle Normal
    Write-Host "   Frontend started." -ForegroundColor Green
} else {
    Write-Host "   Error: Frontend directory not found." -ForegroundColor Red
}

Write-Host "`nAll services launch commands issued." -ForegroundColor Cyan
Write-Host "Please check the individual windows for logs and errors." -ForegroundColor Gray
