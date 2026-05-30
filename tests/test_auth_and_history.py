def test_register_login_and_history_is_user_scoped(client, auth_headers):
    user_a = auth_headers("alice")
    user_b = auth_headers("bob")

    response = client.get("/history", headers=user_a)
    assert response.status_code == 200
    assert response.json() == []

    response = client.get("/history", headers=user_b)
    assert response.status_code == 200
    assert response.json() == []


def test_history_requires_auth(client):
    response = client.get("/history")
    assert response.status_code == 401
