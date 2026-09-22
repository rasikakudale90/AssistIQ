import pytest
from fastapi.testclient import TestClient


def test_download_info_endpoint(client: TestClient):
    """Verifies that GET /api/v1/downloads/info returns metadata and download URLs."""
    response = client.get("/api/v1/downloads/info")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "desktop" in data
    assert "android" in data
    assert "ios" in data
    assert data["desktop"]["filename"] == "AssistIQ-Helpdesk-Setup.exe"
    assert data["android"]["filename"] == "AssistIQ-Mobile.apk"
    assert "/downloads/desktop" in data["desktop"]["download_url"]
    assert "/downloads/android" in data["android"]["download_url"]


def test_download_desktop_endpoint(client: TestClient):
    """Verifies that GET /api/v1/downloads/desktop serves the installer executable if present."""
    response = client.get("/api/v1/downloads/desktop")
    # Should either return 200 (file stream) or 404 with clear message
    if response.status_code == 200:
        assert response.headers.get("content-type") in [
            "application/vnd.microsoft.portable-executable",
            "application/octet-stream",
        ]
        assert "AssistIQ-Helpdesk-Setup.exe" in response.headers.get("content-disposition", "")
    else:
        assert response.status_code == 404


def test_download_android_endpoint(client: TestClient):
    """Verifies that GET /api/v1/downloads/android serves the Android APK package if present."""
    response = client.get("/api/v1/downloads/android")
    if response.status_code == 200:
        assert response.headers.get("content-type") in [
            "application/vnd.android.package-archive",
            "application/octet-stream",
        ]
        assert "AssistIQ-Mobile.apk" in response.headers.get("content-disposition", "")
    else:
        assert response.status_code == 404
