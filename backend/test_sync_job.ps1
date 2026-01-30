# PowerShell 测试脚本 - 同步任务创建 API
# 使用方法: .\test_sync_job.ps1

$baseUrl = "http://localhost:3000/api/v3"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "同步任务元数据验证功能测试" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. 检查服务是否运行
Write-Host "`n[1/3] 检查服务状态..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-WebRequest -Uri "$baseUrl/health/summary" -Method GET -TimeoutSec 2 -ErrorAction Stop
    Write-Host "   ✅ 服务运行正常" -ForegroundColor Green
} catch {
    Write-Host "   ❌ 无法连接到服务" -ForegroundColor Red
    Write-Host "   💡 请确保后端服务运行在 http://localhost:3000" -ForegroundColor Yellow
    Write-Host "      启动命令: cd backend && uvicorn app.main:app --reload --port 3000" -ForegroundColor Yellow
    exit 1
}

# 2. 获取连接列表
Write-Host "`n[2/3] 获取连接列表..." -ForegroundColor Yellow
try {
    $connResponse = Invoke-WebRequest -Uri "$baseUrl/connectors" -Method GET -TimeoutSec 5
    $connections = ($connResponse.Content | ConvertFrom-Json)
    
    if ($connections.Count -gt 0) {
        $connId = $connections[0].id
        $connName = $connections[0].name
        Write-Host "   ✅ 找到连接: $connName (ID: $connId)" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  没有找到连接，使用测试ID" -ForegroundColor Yellow
        $connId = "test_conn_1"
    }
} catch {
    Write-Host "   ⚠️  获取连接失败，使用测试ID" -ForegroundColor Yellow
    $connId = "test_conn_1"
}

# 3. 创建同步任务
Write-Host "`n[3/3] 创建同步任务..." -ForegroundColor Yellow

$payload = @{
    connection_id = $connId
    name = "测试同步任务"
    source_config = @{
        table = "test_table"
    }
    target_table = "raw_test_table_$(Get-Random -Minimum 1000 -Maximum 9999)"
    sync_mode = "FULL_OVERWRITE"
    is_enabled = $true
} | ConvertTo-Json -Depth 10

Write-Host "   请求数据:" -ForegroundColor Gray
Write-Host ($payload | ConvertFrom-Json | ConvertTo-Json -Depth 10) -ForegroundColor Gray

try {
    $response = Invoke-WebRequest -Uri "$baseUrl/sync-jobs" -Method POST -Body $payload -ContentType "application/json" -TimeoutSec 10
    $responseData = $response.Content | ConvertFrom-Json
    
    Write-Host "`n   ✅ 同步任务创建成功！" -ForegroundColor Green
    Write-Host "`n   响应数据:" -ForegroundColor Cyan
    Write-Host ($responseData | ConvertTo-Json -Depth 10) -ForegroundColor White
    
    # 解析警告信息
    if ($responseData.warnings) {
        $warnings = $responseData.warnings
        Write-Host "`n   📋 警告信息:" -ForegroundColor Yellow
        Write-Host "      - 映射存在: $($warnings.mapping_exists)" -ForegroundColor $(if ($warnings.mapping_exists) { "Yellow" } else { "Green" })
        Write-Host "      - 表名不匹配: $($warnings.mapping_table_mismatch)" -ForegroundColor $(if ($warnings.mapping_table_mismatch) { "Yellow" } else { "Green" })
        Write-Host "      - 表已存在: $($warnings.table_exists)" -ForegroundColor $(if ($warnings.table_exists) { "Green" } else { "Gray" })
        
        if ($warnings.mapping_table_mismatch) {
            Write-Host "`n   ⚠️  检测到映射表名不匹配！" -ForegroundColor Red
            Write-Host "      现有映射表名: $($warnings.mapping_table_mismatch)" -ForegroundColor Yellow
            $payloadObj = $payload | ConvertFrom-Json
            Write-Host "      新同步任务表名: $($payloadObj.target_table)" -ForegroundColor Yellow
            Write-Host "      💡 建议：更新映射的表名以匹配新的同步任务" -ForegroundColor Cyan
        }
    }
    
    if ($responseData.job) {
        $job = $responseData.job
        Write-Host "`n   📝 任务信息:" -ForegroundColor Cyan
        Write-Host "      - ID: $($job.id)" -ForegroundColor White
        Write-Host "      - 名称: $($job.name)" -ForegroundColor White
        Write-Host "      - 目标表: $($job.target_table)" -ForegroundColor White
        Write-Host "      - 同步模式: $($job.sync_mode)" -ForegroundColor White
    }
    
} catch {
    Write-Host "`n   ❌ 创建失败" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "   错误信息: $responseBody" -ForegroundColor Red
    } else {
        Write-Host "   错误信息: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "测试完成" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
