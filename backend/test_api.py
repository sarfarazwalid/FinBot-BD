from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Test ambiguous query
response = client.post('/api/v1/chat', json={'message': 'How to reset PIN?'})
print('Ambiguous query "How to reset PIN?":')
print('  Status:', response.status_code)
print('  Answer:', response.json().get('answer'))
print('  Sources:', response.json().get('sources'))
print('  Confidence:', response.json().get('confidence'))
print()

# Test non-ambiguous query
response = client.post('/api/v1/chat', json={'message': 'How to reset bKash PIN?'})
print('Non-ambiguous query "How to reset bKash PIN?":')
print('  Status:', response.status_code)
print('  Answer:', response.json().get('answer')[:100] + '...' if len(response.json().get('answer', '')) > 100 else response.json().get('answer'))
print('  Sources:', response.json().get('sources'))
print('  Confidence:', response.json().get('confidence'))