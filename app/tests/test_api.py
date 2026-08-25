import pytest


@pytest.mark.asyncio
async def test_health(client):
    """
    Test that the health endpoint returns 200 OK.
    This is a simple sanity check to make sure the app is running.
    """
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_register_user(client):
    """
    Test that we can register a new user.
    """
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "testuser@example.com", "password": "testpass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert "id" in data
    assert "hashed_password" not in data  # Security check: never return passwords!


@pytest.mark.asyncio
async def test_login_user(client):
    """
    Test that we can login and get a token.
    """
    # First, register a user
    await client.post(
        "/api/v1/auth/register",
        json={"email": "loginuser@example.com", "password": "testpass123"},
    )

    # Now try to login
    # Note: OAuth2PasswordRequestForm expects form data, not JSON
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "loginuser@example.com", "password": "testpass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
