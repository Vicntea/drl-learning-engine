#!/bin/bash

# ========================================
# CURL EXAMPLES - DRL ENDPOINTS
# ========================================

BASE_URL="http://localhost:8000"

# ========================================
# 1. NEXT-EXERCISE SIN FOCUS
# ========================================
echo "=== 1. Next Exercise (sin focus) ==="
curl -X POST "$BASE_URL/next-exercise" \
  -H "Content-Type: application/json" \
  -d '{
    "student_state": {
      "skill_proficiency": {
        "1a": 0.7,
        "2a": 0.5,
        "2b": 0.3,
        "3a": 0.2
      },
      "preferred_node": null,
      "difficulty": null,
      "free_navigation": true
    },
    "focus": null
  }' | python -m json.tool

echo -e "\n"

# ========================================
# 2. NEXT-EXERCISE CON FOCUS FLEXIBLE
# ========================================
echo "=== 2. Next Exercise (focus flexible) ==="
curl -X POST "$BASE_URL/next-exercise" \
  -H "Content-Type: application/json" \
  -d '{
    "student_state": {
      "skill_proficiency": {
        "1a": 0.7,
        "2a": 0.5,
        "2b": 0.3,
        "3a": 0.2
      },
      "preferred_node": null,
      "difficulty": null,
      "free_navigation": true
    },
    "focus": {
      "nodes": ["2a", "2b"],
      "strict": false
    }
  }' | python -m json.tool

echo -e "\n"

# ========================================
# 3. NEXT-EXERCISE CON FOCUS ESTRICTO
# ========================================
echo "=== 3. Next Exercise (focus ESTRICTO) ==="
curl -X POST "$BASE_URL/next-exercise" \
  -H "Content-Type: application/json" \
  -d '{
    "student_state": {
      "skill_proficiency": {
        "1a": 0.7,
        "2a": 0.5,
        "2b": 0.3,
        "3a": 0.2
      },
      "preferred_node": null,
      "difficulty": null,
      "free_navigation": true
    },
    "focus": {
      "nodes": ["2a", "2b"],
      "strict": true
    }
  }' | python -m json.tool

echo -e "\n"

# ========================================
# 4. SESSION-END
# ========================================
echo "=== 4. Session End (calcular recompensa) ==="
curl -X POST "$BASE_URL/session-end" \
  -H "Content-Type: application/json" \
  -d '{
    "session_events": [
      {
        "node": "1a",
        "correct": true,
        "response_time": 5000,
        "difficulty": 1
      },
      {
        "node": "2a",
        "correct": true,
        "response_time": 8000,
        "difficulty": 2
      },
      {
        "node": "2b",
        "correct": false,
        "response_time": 12000,
        "difficulty": 2
      }
    ]
  }' | python -m json.tool

echo -e "\n"

# ========================================
# 5. SESSION-END CON MÁS EVENTOS
# ========================================
echo "=== 5. Session End (sesión más larga) ==="
curl -X POST "$BASE_URL/session-end" \
  -H "Content-Type: application/json" \
  -d '{
    "session_events": [
      {
        "node": "1a",
        "correct": true,
        "response_time": 3000,
        "difficulty": 1
      },
      {
        "node": "1a",
        "correct": true,
        "response_time": 2500,
        "difficulty": 1
      },
      {
        "node": "2a",
        "correct": true,
        "response_time": 7000,
        "difficulty": 2
      },
      {
        "node": "2a",
        "correct": false,
        "response_time": 15000,
        "difficulty": 3
      },
      {
        "node": "2b",
        "correct": true,
        "response_time": 9000,
        "difficulty": 2
      }
    ]
  }' | python -m json.tool

echo -e "\n===== DONE ====="
