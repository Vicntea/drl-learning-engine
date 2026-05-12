# ========================================
# CURL EXAMPLES - DRL ENDPOINTS (PowerShell)
# ========================================

$BASE_URL = "http://localhost:8000"

# ========================================
# 1. NEXT-EXERCISE SIN FOCUS
# ========================================
Write-Host "=== 1. Next Exercise (sin focus) ===" -ForegroundColor Green

$body1 = @{
    student_state = @{
        skill_proficiency = @{
            "1a" = 0.7
            "2a" = 0.5
            "2b" = 0.3
            "3a" = 0.2
        }
        preferred_node = $null
        difficulty = $null
        free_navigation = $true
    }
    focus = $null
} | ConvertTo-Json

Invoke-WebRequest -Uri "$BASE_URL/next-exercise" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body1 | Select-Object -ExpandProperty Content | ConvertFrom-Json | ConvertTo-Json

Write-Host "`n"

# ========================================
# 2. NEXT-EXERCISE CON FOCUS FLEXIBLE
# ========================================
Write-Host "=== 2. Next Exercise (focus flexible) ===" -ForegroundColor Green

$body2 = @{
    student_state = @{
        skill_proficiency = @{
            "1a" = 0.7
            "2a" = 0.5
            "2b" = 0.3
            "3a" = 0.2
        }
        preferred_node = $null
        difficulty = $null
        free_navigation = $true
    }
    focus = @{
        nodes = @("2a", "2b")
        strict = $false
    }
} | ConvertTo-Json

Invoke-WebRequest -Uri "$BASE_URL/next-exercise" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body2 | Select-Object -ExpandProperty Content | ConvertFrom-Json | ConvertTo-Json

Write-Host "`n"

# ========================================
# 3. NEXT-EXERCISE CON FOCUS ESTRICTO
# ========================================
Write-Host "=== 3. Next Exercise (focus ESTRICTO) ===" -ForegroundColor Green

$body3 = @{
    student_state = @{
        skill_proficiency = @{
            "1a" = 0.7
            "2a" = 0.5
            "2b" = 0.3
            "3a" = 0.2
        }
        preferred_node = $null
        difficulty = $null
        free_navigation = $true
    }
    focus = @{
        nodes = @("2a", "2b")
        strict = $true
    }
} | ConvertTo-Json

Invoke-WebRequest -Uri "$BASE_URL/next-exercise" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body3 | Select-Object -ExpandProperty Content | ConvertFrom-Json | ConvertTo-Json

Write-Host "`n"

# ========================================
# 4. SESSION-END
# ========================================
Write-Host "=== 4. Session End (calcular recompensa) ===" -ForegroundColor Green

$body4 = @{
    session_events = @(
        @{
            node = "1a"
            correct = $true
            response_time = 5000
            difficulty = 1
        },
        @{
            node = "2a"
            correct = $true
            response_time = 8000
            difficulty = 2
        },
        @{
            node = "2b"
            correct = $false
            response_time = 12000
            difficulty = 2
        }
    )
} | ConvertTo-Json

Invoke-WebRequest -Uri "$BASE_URL/session-end" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body4 | Select-Object -ExpandProperty Content | ConvertFrom-Json | ConvertTo-Json

Write-Host "`n"

# ========================================
# 5. SESSION-END CON MÁS EVENTOS
# ========================================
Write-Host "=== 5. Session End (sesión más larga) ===" -ForegroundColor Green

$body5 = @{
    session_events = @(
        @{
            node = "1a"
            correct = $true
            response_time = 3000
            difficulty = 1
        },
        @{
            node = "1a"
            correct = $true
            response_time = 2500
            difficulty = 1
        },
        @{
            node = "2a"
            correct = $true
            response_time = 7000
            difficulty = 2
        },
        @{
            node = "2a"
            correct = $false
            response_time = 15000
            difficulty = 3
        },
        @{
            node = "2b"
            correct = $true
            response_time = 9000
            difficulty = 2
        }
    )
} | ConvertTo-Json

Invoke-WebRequest -Uri "$BASE_URL/session-end" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body5 | Select-Object -ExpandProperty Content | ConvertFrom-Json | ConvertTo-Json

Write-Host "`n===== DONE =====" -ForegroundColor Green
