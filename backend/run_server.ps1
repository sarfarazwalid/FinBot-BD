# FinBot BD Backend Startup Script
# Ensures dependencies are installed and starts uvicorn

Write-Host "Installing backend dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt

Write-Host "`nStarting FinBot BD API..." -ForegroundColor Green
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000