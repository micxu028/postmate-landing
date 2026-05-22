"""Tests for brands router — create, read brand info."""
import pytest


@pytest.mark.asyncio
async def test_create_brand_success(client, registered_user):
    resp = await client.post("/api/brands", json={
        "name": "FitFlow Yoga",
        "industry": "fitness",
        "style": "energetic",
        "tone": "inspirational",
        "post_frequency": 3,
        "image_urls": ["https://example.com/img.jpg"],
    }, headers={"Authorization": f"Bearer {registered_user['token']}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "FitFlow Yoga"
    assert data["industry"] == "fitness"
    assert data["has_images"] is True
    assert "id" in data


@pytest.mark.asyncio
async def test_create_brand_no_auth(client):
    resp = await client.post("/api/brands", json={
        "name": "No Auth Studio",
        "industry": "fitness",
        "style": "professional",
        "tone": "professional",
        "post_frequency": 3,
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_create_brand_invalid_industry(client, registered_user):
    resp = await client.post("/api/brands", json={
        "name": "Bad Industry",
        "industry": "restaurant",
        "style": "warm",
        "tone": "friendly",
        "post_frequency": 3,
    }, headers={"Authorization": f"Bearer {registered_user['token']}"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_get_my_brand(client, registered_user):
    # Create first
    await client.post("/api/brands", json={
        "name": "My Studio",
        "industry": "yoga",
        "style": "minimalist",
        "tone": "friendly",
        "post_frequency": 5,
    }, headers={"Authorization": f"Bearer {registered_user['token']}"})

    resp = await client.get("/api/brands/me", headers={
        "Authorization": f"Bearer {registered_user['token']}"
    })
    assert resp.status_code == 200
    assert resp.json()["name"] == "My Studio"


@pytest.mark.asyncio
async def test_get_my_brand_not_found(client, registered_user):
    resp = await client.get("/api/brands/me", headers={
        "Authorization": f"Bearer {registered_user['token']}"
    })
    assert resp.status_code == 404
