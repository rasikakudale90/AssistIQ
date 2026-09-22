import os
import socket
from pathlib import Path
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import FileResponse

router = APIRouter(prefix="/downloads", tags=["App Downloads & Installers"])

# Project root resolution
BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent


def get_local_ip() -> str:
    """Discovers the active local LAN IPv4 address for QR code downloads."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def get_desktop_installer_path() -> Path:
    """Finds the compiled Windows setup executable."""
    candidates = [
        PROJECT_ROOT / "frontend" / "dist-desktop" / "AssistIQ Helpdesk Setup 1.0.0.exe",
        PROJECT_ROOT / "frontend" / "dist-desktop" / "AssistIQ-Helpdesk-Setup.exe",
        PROJECT_ROOT / "AssistIQ-Desktop" / "AssistIQ-win32-x64" / "AssistIQ.exe",
    ]
    for p in candidates:
        if p.exists():
            return p
    # Fallback to any .exe in dist-desktop
    dist_dir = PROJECT_ROOT / "frontend" / "dist-desktop"
    if dist_dir.exists():
        for f in dist_dir.glob("*.exe"):
            return f
    return candidates[0]


def get_android_apk_path() -> Path:
    """Finds the compiled Android APK package (prefers optimized release build)."""
    candidates = [
        PROJECT_ROOT / "flutter_app" / "build" / "app" / "outputs" / "flutter-apk" / "app-release.apk",
        PROJECT_ROOT / "flutter_app" / "build" / "app" / "outputs" / "flutter-apk" / "app-debug.apk",
    ]
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]


@router.get("/info", response_model=Dict[str, Any])
def get_download_info(request: Request):
    """
    Returns download availability, metadata, and local LAN QR-code URLs for mobile & desktop clients.
    """
    local_ip = get_local_ip()
    host = request.headers.get("host", f"{local_ip}:8000")
    base_url = f"http://{host}/api/v1/downloads"
    lan_base_url = f"http://{local_ip}:8000/api/v1/downloads"

    desktop_path = get_desktop_installer_path()
    android_path = get_android_apk_path()

    desktop_exists = desktop_path.exists()
    android_exists = android_path.exists()

    desktop_size_mb = round(os.path.getsize(desktop_path) / (1024 * 1024), 1) if desktop_exists else 0
    android_size_mb = round(os.path.getsize(android_path) / (1024 * 1024), 1) if android_exists else 0

    return {
        "version": "1.0.0",
        "local_ip": local_ip,
        "desktop": {
            "available": desktop_exists,
            "filename": "AssistIQ-Helpdesk-Setup.exe",
            "size_mb": desktop_size_mb,
            "download_url": f"{base_url}/desktop",
            "lan_download_url": f"{lan_base_url}/desktop",
            "platform": "Windows 10/11 (64-bit)",
        },
        "android": {
            "available": android_exists,
            "filename": "AssistIQ-Mobile.apk",
            "size_mb": android_size_mb,
            "download_url": f"{base_url}/android",
            "lan_download_url": f"{lan_base_url}/android",
            "platform": "Android 10+ (ARM64/x86)",
        },
        "ios": {
            "available": True,
            "type": "PWA",
            "platform": "iOS Safari (Add to Home Screen)",
        },
    }


@router.api_route("/desktop", methods=["GET", "HEAD"])
def download_desktop():
    """
    Downloads the official Windows Desktop Application Setup installer.
    """
    desktop_path = get_desktop_installer_path()
    if not desktop_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Desktop installer package is currently compiling or not found.",
        )
    return FileResponse(
        path=str(desktop_path),
        filename="AssistIQ-Helpdesk-Setup.exe",
        media_type="application/vnd.microsoft.portable-executable",
    )


@router.api_route("/android", methods=["GET", "HEAD"])
def download_android():
    """
    Downloads the official Android Mobile APK package for physical mobile devices.
    """
    android_path = get_android_apk_path()
    if not android_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Android APK package is currently compiling or not found.",
        )
    return FileResponse(
        path=str(android_path),
        filename="AssistIQ-Mobile.apk",
        media_type="application/vnd.android.package-archive",
    )
