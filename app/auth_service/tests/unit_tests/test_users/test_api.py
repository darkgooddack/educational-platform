import pytest
import json
import pytest

@pytest.mark.asyncio
async def test_login_user_invalid_credentials(ac):
    response = await ac.post("/users/login", data={
        "username": "nonexistent@example.com",
        "password": "wrongpassword"
    })

    assert response.status_code == 500
    assert response.json()["detail"] == "Invalid credentials"

@pytest.mark.asyncio
async def test_refresh_token_success(ac):
    def open_mock_json(model: str):
        with open(f"tests/{model}.json", encoding="utf-8") as file:
            return json.load(file)

    tokens = open_mock_json("mock_user_tokens")
    refresh_token = tokens[0]["refresh_token"]
    
    response = await ac.post("/users/refresh", headers={"Refresh-Token": refresh_token})
    
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}, response: {response.json()}"
    assert "access_token" in response.json(), f"Response: {response.json()}"

@pytest.mark.asyncio
async def test_verify_invalid_token(ac):
    invalid_token = "invalid_token"
    
    response = await ac.get("/users/verify-token", headers={"access_token": invalid_token})
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"
