import os
import requests
from pathlib import Path

SUPABASE_URL = "https://zmohmutvxwafpwvjdazf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inptb2htdXR2eHdhZnB3dmpkYXpmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc5MDA1Nzc1MSwiZXhwIjoyMTA1NjMzNzUxfQ.g-ZTaV3KwU9d-mOuXK4n5cOEik3eUFOSc2fkkbFuybM"
BUCKET = "assistiq-downloads"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APK_DIR = PROJECT_ROOT / "flutter_app" / "build" / "app" / "outputs" / "flutter-apk"

def upload_file(local_path: Path, remote_filename: str):
    if not local_path.exists():
        print(f"File not found: {local_path}")
        return False

    size_mb = os.path.getsize(local_path) / (1024 * 1024)
    print(f"Uploading {local_path.name} ({size_mb:.2f} MB) as '{remote_filename}'...")

    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{remote_filename}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "apikey": SUPABASE_KEY,
        "x-upsert": "true",
        "Content-Type": "application/vnd.android.package-archive",
        "cache-control": "max-age=0, no-cache, no-store, must-revalidate",
    }

    with open(local_path, "rb") as f:
        res = requests.post(url, headers=headers, data=f)

    if res.status_code in [200, 201]:
        print(f"Successfully uploaded {remote_filename}! Public URL: {SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{remote_filename}")
        return True
    else:
        print(f"Failed to upload {remote_filename}: {res.status_code} - {res.text}")
        return False

if __name__ == "__main__":
    arm64_apk = APK_DIR / "app-arm64-v8a-release.apk"
    if arm64_apk.exists():
        upload_file(arm64_apk, "AssistIQ-Mobile.apk")
        upload_file(arm64_apk, "app-arm64-v8a-release.apk")

    v7a_apk = APK_DIR / "app-armeabi-v7a-release.apk"
    if v7a_apk.exists():
        upload_file(v7a_apk, "app-armeabi-v7a-release.apk")

    x86_apk = APK_DIR / "app-x86_64-release.apk"
    if x86_apk.exists():
        upload_file(x86_apk, "app-x86_64-release.apk")
