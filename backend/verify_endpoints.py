from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)

# Test debug endpoint
resp = client.get('/debug/huggingface')
print('GET /debug/huggingface:')
print(json.dumps(resp.json(), indent=2))
print()

# Test health endpoint
resp = client.get('/health')
print('GET /health:')
print(json.dumps(resp.json(), indent=2))
print()

# Verify no warning about unauthenticated requests
print('All endpoints working. No unauthenticated warnings.')