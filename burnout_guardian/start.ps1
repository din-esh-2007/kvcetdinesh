# Burnout Guardian - Quick Start Script for Windows
# Run this script to set up and start the system

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 59 -ForegroundColor Cyan
Write-Host "🧠 BURNOUT GUARDIAN - QUICK START" -ForegroundColor Cyan
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 59 -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "📋 Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.(10|11|12)") {
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Python 3.10+ required. Current: $pythonVersion" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
if (!(Test-Path "venv")) {
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✅ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "🔌 Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host ""
Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt
Write-Host "✅ Dependencies installed" -ForegroundColor Green

# Create .env file
Write-Host ""
Write-Host "⚙️  Setting up environment..." -ForegroundColor Yellow
if (!(Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "✅ .env file created (please update with your settings)" -ForegroundColor Green
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

# Create directories
Write-Host ""
Write-Host "📁 Creating directories..." -ForegroundColor Yellow
$directories = @("data", "logs", "reports", "models/trained", ".cache")
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Host "✅ Directories created" -ForegroundColor Green

# Generate synthetic dataset
Write-Host ""
Write-Host "🔄 Generating synthetic dataset..." -ForegroundColor Yellow
Write-Host "   This will create 200 employees × 120 days = 24,000 rows" -ForegroundColor Gray
python backend/dataset_generator.py
Write-Host "✅ Dataset generated" -ForegroundColor Green

# Initialize database
Write-Host ""
Write-Host "🗄️  Initializing database..." -ForegroundColor Yellow
Write-Host "   NOTE: Make sure PostgreSQL is running!" -ForegroundColor Gray
python backend/database.py
Write-Host "✅ Database initialized" -ForegroundColor Green

# Start the application
Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 59 -ForegroundColor Cyan
Write-Host "🚀 STARTING BURNOUT GUARDIAN" -ForegroundColor Cyan
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 59 -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 Application will be available at:" -ForegroundColor Yellow
Write-Host "   Frontend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "   Health:   http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Start uvicorn
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
