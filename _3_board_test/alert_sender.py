import requests

N8N_URL = "http://localhost:5678/webhook-test/68247e60-fe0e-47fc-8a9e-0299812a4167"
STUDENT = "심희현"

data = {
    "student": STUDENT,
    "alerts": [
        {"ip": "192.168.0.10", "level": 10, "rule": 5712},
        {"ip": "192.168.0.15", "level": 5, "rule": 1002}
    ]
}

try:
    res = requests.post(N8N_URL, json=data)
    print(f"[n8n] POST {N8N_URL} -> {res.status_code}")
except Exception as e:
    print(f"[에러] 전송 실패: {e}")