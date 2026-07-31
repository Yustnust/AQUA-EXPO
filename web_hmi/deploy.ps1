# AQUA-EXPO Web HMI Windows 部署脚本
# 用途：构建前端 + 启动后端服务
# 用法：在 PowerShell 中运行 .\deploy.ps1

param(
    [switch]$Build,      # 是否重新构建前端
    [switch]$Start,      # 是否启动服务
    [switch]$Install     # 安装 Python 依赖
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $ScriptDir "backend"
$FrontendDir = Join-Path $ScriptDir "frontend"
$StaticDir = Join-Path $BackendDir "static"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " AQUA-EXPO Web HMI 部署工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 安装 Python 依赖
if ($Install) {
    Write-Host "[1/3] 安装 Python 依赖..." -ForegroundColor Yellow
    Push-Location $BackendDir
    try {
        pip install -r requirements.txt
        Write-Host "  依赖安装完成" -ForegroundColor Green
    }
    catch {
        Write-Host "  依赖安装失败: $_" -ForegroundColor Red
        exit 1
    }
    finally {
        Pop-Location
    }
}

# 2. 构建前端
if ($Build) {
    Write-Host "[2/3] 构建前端..." -ForegroundColor Yellow
    Push-Location $FrontendDir
    
    # 检查 Node.js
    $nodeVersion = node --version 2>$null
    if (-not $nodeVersion) {
        Write-Host "  错误: 未找到 Node.js，请先安装 Node.js" -ForegroundColor Red
        Pop-Location
        exit 1
    }
    Write-Host "  Node.js 版本: $nodeVersion" -ForegroundColor Gray
    
    # 安装依赖（如果需要）
    if (-not (Test-Path "node_modules")) {
        Write-Host "  安装前端依赖..." -ForegroundColor Gray
        npm install
    }
    
    # 构建
    Write-Host "  编译中..." -ForegroundColor Gray
    npm run build
    
    # 复制到后端 static 目录
    Write-Host "  复制静态文件到后端..." -ForegroundColor Gray
    if (Test-Path $StaticDir) {
        Remove-Item -Recurse -Force $StaticDir
    }
    Copy-Item -Recurse "dist" $StaticDir
    
    Write-Host "  前端构建完成" -ForegroundColor Green
    Pop-Location
}

# 3. 启动后端
if ($Start) {
    Write-Host "[3/3] 启动后端服务..." -ForegroundColor Yellow
    Push-Location $BackendDir
    
    # 创建必要的目录
    if (-not (Test-Path "data")) { New-Item -ItemType Directory -Path "data" | Out-Null }
    if (-not (Test-Path "logs")) { New-Item -ItemType Directory -Path "logs" | Out-Null }
    
    Write-Host "  启动 uvicorn 服务..." -ForegroundColor Gray
    Write-Host "  访问地址: http://localhost:8000" -ForegroundColor Green
    Write-Host ""
    
    uvicorn app.main:app --host 0.0.0.0 --port 8000
    
    Pop-Location
}

Write-Host ""
Write-Host "完成!" -ForegroundColor Green
Write-Host ""
Write-Host "使用示例:" -ForegroundColor Gray
Write-Host "  .\deploy.ps1 -Install -Build -Start   # 首次部署：安装依赖 + 构建前端 + 启动" -ForegroundColor Gray
Write-Host "  .\deploy.ps1 -Build -Start            # 更新前端后重新部署" -ForegroundColor Gray
Write-Host "  .\deploy.ps1 -Start                   # 仅启动后端" -ForegroundColor Gray