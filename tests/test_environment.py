def test_environment_route(client):
    response = client.get('/environment')
    assert response.status_code == 200
    assert b"Current environment" in response.data