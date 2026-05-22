"""Tests for posts router — reading generated posts."""
import pytest


@pytest.mark.asyncio
async def test_get_posts_no_brand(client, registered_user):
    resp = await client.get("/api/posts", headers={
        "Authorization": f"Bearer {registered_user['token']}"
    })
    # No brand yet, should return empty or 404
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_get_posts_no_auth(client):
    resp = await client.get("/api/posts")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_generate_no_brand(client, registered_user):
    resp = await client.post("/api/generate", headers={
        "Authorization": f"Bearer {registered_user['token']}"
    })
    assert resp.status_code == 400
    assert "onboarding" in resp.json()["detail"].lower()
