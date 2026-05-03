import sys
sys.path.insert(0, '.')
from wsgi import app
import json

client = app.test_client()
r = client.post('/api/v1/query', json={'query': 'temp', 'user_id': 'test'}, content_type='application/json')
data = json.loads(r[0])
print('API analysis keys:', list(data['result']['analysis'].keys()))
print('Has insights?', 'insights' in data['result']['analysis'])
if 'insights' in data['result']['analysis']:
    print('Insights value:', data['result']['analysis']['insights'])
else:
    print('NO INSIGHTS ARRAY FOUND')
    print('Full analysis:', data['result']['analysis'])
