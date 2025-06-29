# PowerShell deployment script for Windows/local development

Write-Host "🚀 Setting up GenAI CSV Enhancer locally..." -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+ first." -ForegroundColor Red
    exit 1
}

# Check if pip is available
try {
    pip --version | Out-Null
    Write-Host "✅ pip is available" -ForegroundColor Green
} catch {
    Write-Host "❌ pip not found. Please ensure pip is installed." -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
try {
    pip install -r requirements.txt
    Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install dependencies. Check requirements.txt" -ForegroundColor Red
    exit 1
}

# Check AWS configuration
Write-Host "🔧 Checking AWS configuration..." -ForegroundColor Yellow
try {
    aws sts get-caller-identity | Out-Null
    Write-Host "✅ AWS credentials configured" -ForegroundColor Green
} catch {
    Write-Host "⚠️ AWS credentials not configured. Please run 'aws configure' or set environment variables:" -ForegroundColor Yellow
    Write-Host "   set AWS_ACCESS_KEY_ID=your_key" -ForegroundColor Gray
    Write-Host "   set AWS_SECRET_ACCESS_KEY=your_secret" -ForegroundColor Gray
    Write-Host "   set AWS_DEFAULT_REGION=us-east-1" -ForegroundColor Gray
}

# Create startup script
$startupScript = @"
@echo off
echo Starting GenAI CSV Enhancer...
streamlit run main.py
pause
"@

$startupScript | Out-File -FilePath "start-app.bat" -Encoding ascii
Write-Host "✅ Created start-app.bat for easy launching" -ForegroundColor Green

Write-Host ""
Write-Host "🎉 Setup complete! To start the application:" -ForegroundColor Green
Write-Host "   Option 1: Double-click start-app.bat" -ForegroundColor Cyan
Write-Host "   Option 2: Run 'streamlit run main.py'" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Yellow
Write-Host "   1. Ensure AWS Bedrock access is configured" -ForegroundColor Gray
Write-Host "   2. Request access to Claude 3 Sonnet in AWS Console" -ForegroundColor Gray
Write-Host "   3. Upload a CSV file to test the application" -ForegroundColor Gray
Write-Host ""
Write-Host "🌐 The app will open at: http://localhost:8501" -ForegroundColor Cyan
