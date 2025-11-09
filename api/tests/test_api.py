from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_session_lifecycle():
    response = client.post('/api/session/new')
    assert response.status_code == 200
    data = response.json()
    session_id = data['session_id']

    gate_response = client.post('/api/gate/apply', json={'session_id': session_id, 'gate': 'H'})
    assert gate_response.status_code == 200

    gate_response = client.post('/api/gate/apply', json={'session_id': session_id, 'gate': 'CNOT'})
    assert gate_response.status_code == 200

    trials_response = client.post('/api/trials', json={'session_id': session_id, 'qubit': 'BOTH', 'n': 500})
    assert trials_response.status_code == 200
    trials = trials_response.json()
    assert set(trials['counts'].keys()).issubset({'00', '11'})

    measure_response = client.post('/api/measure', json={'session_id': session_id, 'qubit': 'Q1'})
    assert measure_response.status_code == 200
    outcome = measure_response.json()['outcome']
    assert outcome['Q1'] in (0, 1)

    reset_response = client.post('/api/reset', json={'session_id': session_id, 'qubit': 'Q1'})
    assert reset_response.status_code == 200

    hard_reset_response = client.post('/api/reset/hard', json={'session_id': session_id})
    assert hard_reset_response.status_code == 200
