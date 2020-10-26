def test_index(client):
    response = client.get('/haskell')
    assert b'haskell' in response.data
