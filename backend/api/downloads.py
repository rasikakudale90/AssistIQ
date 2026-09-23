import os
import socket
from pathlib import Path
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import FileResponse, RedirectResponse

router = APIRouter(prefix="/downloads", tags=["App Downloads & Installers"])

# Project root resolution
BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent

# Cloud Public CDN/Storage URLs
CLOUD_ANDROID_APK_URL = "https://zmohmutvxwafpwvjdazf.supabase.co/storage/v1/object/public/assistiq-downloads/AssistIQ-Mobile.apk?v=1.0.1"
CLOUD_DESKTOP_EXE_URL = "https://github.com/rasikakudale90/AssistIQ/releases/download/v1.0.0/AssistIQ-Helpdesk-Setup.exe?v=1.0.1"


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
    """Finds the compiled Android APK package (prefers optimized split or release build)."""
    candidates = [
        PROJECT_ROOT / "flutter_app" / "build" / "app" / "outputs" / "flutter-apk" / "app-arm64-v8a-release.apk",
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
    scheme = "https" if "render.com" in host or "vercel.app" in host or request.headers.get("x-forwarded-proto") == "https" else "http"
    base_url = f"{scheme}://{host}/api/v1/downloads"
    lan_base_url = f"http://{local_ip}:8000/api/v1/downloads"

    desktop_path = get_desktop_installer_path()
    android_path = get_android_apk_path()

    desktop_exists = desktop_path.exists()
    android_exists = android_path.exists()

    desktop_size_mb = round(os.path.getsize(desktop_path) / (1024 * 1024), 1) if desktop_exists else 108.0
    android_size_mb = round(os.path.getsize(android_path) / (1024 * 1024), 1) if android_exists else 18.5

    # If running in cloud production, provide direct public cloud URLs for QR codes
    is_cloud = "render.com" in host or "vercel.app" in host
    mobile_qr_url = CLOUD_ANDROID_APK_URL if is_cloud else f"{lan_base_url}/android"

    return {
        "version": "1.0.0",
        "local_ip": local_ip,
        "desktop": {
            "available": True,
            "filename": "AssistIQ-Helpdesk-Setup.exe",
            "size_mb": desktop_size_mb,
            "download_url": f"{base_url}/desktop",
            "lan_download_url": f"{lan_base_url}/desktop",
            "direct_url": CLOUD_DESKTOP_EXE_URL,
            "platform": "Windows 10/11 (64-bit)",
        },
        "android": {
            "available": True,
            "filename": "AssistIQ-Mobile.apk",
            "size_mb": android_size_mb,
            "download_url": f"{base_url}/android",
            "lan_download_url": f"{lan_base_url}/android",
            "direct_url": CLOUD_ANDROID_APK_URL,
            "qr_url": mobile_qr_url,
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
    Streams local file if present; otherwise redirects to cloud release binary.
    """
    desktop_path = get_desktop_installer_path()
    if desktop_path.exists():
        return FileResponse(
            path=str(desktop_path),
            filename="AssistIQ-Helpdesk-Setup.exe",
            media_type="application/vnd.microsoft.portable-executable",
        )
    return RedirectResponse(
        url=CLOUD_DESKTOP_EXE_URL,
        status_code=status.HTTP_302_FOUND,
    )


@router.api_route("/android", methods=["GET", "HEAD"])
def download_android():
    """
    Downloads the official Android Mobile APK package for physical mobile devices.
    Streams local file if present; otherwise redirects to Supabase cloud CDN binary.
    """
    android_path = get_android_apk_path()
    if android_path.exists():
        return FileResponse(
            path=str(android_path),
            filename="AssistIQ-Mobile.apk",
            media_type="application/vnd.android.package-archive",
        )
    return RedirectResponse(
        url=CLOUD_ANDROID_APK_URL,
        status_code=status.HTTP_302_FOUND,
    )
