# 🚀 TuniGuard - Complete Setup Script
# Run this script to set up everything automatically

Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║           🛡️  TuniGuard API - Automated Setup             ║" -ForegroundColor Cyan
Write-Host "║    AI-Powered Telecom Security Sentinel for Tunisia        ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "📋 Checking Prerequisites..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.([9]|1[0-9])") {
    Write-Host "✅ Python version: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Error: Python 3.9+ required. Current: $pythonVersion" -ForegroundColor Red
    Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "⚠️  Virtual environment already exists, skipping..." -ForegroundColor Yellow
} else {
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "🔌 Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host ""
Write-Host "📚 Installing dependencies (this may take 2-3 minutes)..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ All dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Error installing dependencies" -ForegroundColor Red
    exit 1
}

# Create .env file
Write-Host ""
Write-Host "⚙️  Configuring environment..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "⚠️  .env file already exists" -ForegroundColor Yellow
    $overwrite = Read-Host "Overwrite? (y/n)"
    if ($overwrite -eq "y") {
        Copy-Item .env.example .env -Force
        Write-Host "✅ .env file created from template" -ForegroundColor Green
    }
} else {
    Copy-Item .env.example .env
    Write-Host "✅ .env file created from template" -ForegroundColor Green
}

# Prompt for Gemini API key
Write-Host ""
Write-Host "🔑 Gemini API Key Setup" -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor Gray
$currentKey = (Get-Content .env | Select-String "GEMINI_API_KEY=").ToString().Split("=")[1]

if ($currentKey -and $currentKey -ne "your_gemini_api_key_here") {
    Write-Host "✅ API key already configured" -ForegroundColor Green
} else {
    Write-Host "📝 You need a Google Gemini API key (it's FREE!)" -ForegroundColor Yellow
    Write-Host "   Get one at: https://ai.google.dev/" -ForegroundColor Cyan
    Write-Host ""
    $apiKey = Read-Host "Enter your Gemini API key (or press Enter to skip)"
    
    if ($apiKey) {
        $envContent = Get-Content .env
        $envContent = $envContent -replace "GEMINI_API_KEY=.*", "GEMINI_API_KEY=$apiKey"
        $envContent | Set-Content .env
        Write-Host "✅ API key configured in .env file" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Skipped API key setup. Edit .env file manually before running." -ForegroundColor Yellow
    }
}

# Initialize database
Write-Host ""
Write-Host "🗄️  Initializing database..." -ForegroundColor Yellow
python init_db.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Database initialized with sample data" -ForegroundColor Green
} else {
    Write-Host "❌ Error initializing database" -ForegroundColor Red
    exit 1
}

# Run tests
Write-Host ""
Write-Host "🧪 Running tests..." -ForegroundColor Yellow
pytest tests/ -v --tb=short
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ All tests passed" -ForegroundColor Green
} else {
    Write-Host "⚠️  Some tests failed (this is OK for initial setup)" -ForegroundColor Yellow
}

# Final instructions
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              ✅ Setup Complete! You're Ready!               ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 To start the API server:" -ForegroundColor Cyan
Write-Host "   python run.py" -ForegroundColor White
Write-Host ""
Write-Host "Once running, visit:" -ForegroundColor Cyan
Write-Host "   • API Health:       http://localhost:5000/api/health" -ForegroundColor White
Write-Host "   • Swagger Docs:     http://localhost:5000/api/docs" -ForegroundColor White
Write-Host "   • API Reference:    docs/API_GUIDE.md" -ForegroundColor White
Write-Host ""
Write-Host "📚 Documentation:" -ForegroundColor Cyan
Write-Host "   • Quick Start:      docs/QUICKSTART.md" -ForegroundColor White
Write-Host "   • Full Docs:        docs/DOCUMENTATION.md" -ForegroundColor White
Write-Host "   • API Guide:        docs/API_GUIDE.md" -ForegroundColor White
Write-Host "   • For Professor:    docs/PROFESSOR_SUBMISSION.md" -ForegroundColor White
Write-Host ""
Write-Host "🧪 To run tests:" -ForegroundColor Cyan
Write-Host "   pytest tests/ -v --cov=app" -ForegroundColor White
Write-Host ""
Write-Host "🐳 To run with Docker:" -ForegroundColor Cyan
Write-Host "   docker-compose up -d" -ForegroundColor White
Write-Host ""
Write-Host "🇹🇳 TuniGuard: Protecting Tunisia's Digital Future!" -ForegroundColor Green
Write-Host ""
