from fastapi.testclient import TestClient
from ledgerlens.api import app

client=TestClient(app)


def test_demo_import_analyze_and_evidence_workflow():
 demo=client.get('/api/demo')
 assert demo.status_code==200
 payload=demo.json()
 result=client.post('/api/analyze',json=payload)
 assert result.status_code==200
 assert result.json()['data_label']=='DEMO DATA'
 assert result.json()['metrics']['gross_margin']==.4
 imported=client.post('/api/import',content=__import__('json').dumps(payload['companyfacts']))
 assert imported.status_code==200
 assert imported.json()['metadata']['source']=='USER PROVIDED DATA'


def test_invalid_json_context_and_large_body_fail_honestly():
 assert client.post('/api/import',content='not json').status_code==422
 payload=client.get('/api/demo').json();payload['query']['tax_rate']=2
 assert client.post('/api/analyze',json=payload).status_code==422
 payload=client.get('/api/demo').json();payload['query']['as_of']='2025-12-31'
 response=client.post('/api/analyze',json=payload)
 assert response.status_code==422
 assert 'revenue' in response.json()['detail']
 assert client.post('/api/import',content=b'x'*10000001).status_code==413


def test_fetch_requires_real_identifying_contact():
 assert client.post('/api/fetch',json={'cik':1,'user_agent':'bad'}).status_code==422
 assert client.get('/health').json()['status']=='ok'
