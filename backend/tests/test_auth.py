"""Tests for auth router — register, login, token validation."""
import pytest


@pytest.mark.asyncio
async def test_register_success(client):
    resp = await client.post("/api/auth/register", json={
        "email": "new@studio.com",
        "password": "secret1234",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "token" in data
    assert "user_id" in data
    assert len(data["token"]) > 20


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    await client.post("/api/auth/register", json={
        "email": "dup@studio.com",
        "password": "secret1234",
    })
    resp = await client.post("/api/auth/register", json={
        "email": "dup@studio.com",
        "password": "otherpass123",
    })
    assert resp.status_code == 409
    assert "already" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_short_password(client):
    resp = await client.post("/api/auth/register", json={
        "email": "short@studio.com",
        "password": "123",
    })
    assert resp.status_code == 422
    assert resp.json()["detail"][0]["type"] in ("value_error", "string_too_short")

@pytest.mark.asyncio
async def test_register_empty_password(client):
    resp = await client.post("/api/auth/register", json={
        "email": "empty@studio.com",
        "password": "",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client):
    await client.post("/api/auth/register", json={
        "email": "login@studio.com",
        "password": "mypassword",
    })
    resp = await client.post("/api/auth/login", json={
        "email": "login@studio.com",
        "password": "mypassword",
    })
    assert resp.status_code == 200
    assert "token" in resp.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/api/auth/register", json={
        "email": "wrong@studio.com",
        "password": "correctpass",
    })
    resp = await client.post("/api/auth/login", json={
        "email": "wrong@studio.com",
        "password": "wrongpass",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    resp = await client.post("/api/auth/login", json={
        "email": "nobody@studio.com",
        "password": "somepass",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_health_check(client):
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
