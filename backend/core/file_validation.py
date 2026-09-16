import os
from typing import Set, Tuple
from backend.core.errors import ValidationException

# Constraints per SRS §7.5
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024       # 10 MB per file
MAX_CASE_TOTAL_BYTES = 50 * 1024 * 1024     # 50 MB per case

ALLOWED_EXTENSIONS: Set[str] = {
    "jpg",
    "jpeg",
    "png",
    "webp",
    "gif",
    "pdf",
    "docx",
    "txt",
    "log",
}

# Magic byte signatures
MAGIC_SIGNATURES = {
    "jpg": [b"\xFF\xD8\xFF"],
    "jpeg": [b"\xFF\xD8\xFF"],
    "png": [b"\x89PNG\r\n\x1a\n"],
    "gif": [b"GIF87a", b"GIF89a"],
    "pdf": [b"%PDF-"],
    "docx": [b"PK\x03\x04"],  # Zip container
}


def validate_file_content(file_name: str, file_bytes: bytes, current_case_total_bytes: int = 0) -> Tuple[str, str]:
    """
    Validates file size, extension, and header magic bytes per SRS §7.5.
    Returns (cleaned_extension, mime_type).
    Raises ValidationException on any violation.
    """
    # 1. Size check
    file_size = len(file_bytes)
    if file_size == 0:
        raise ValidationException("File is empty (0 bytes).")
    if file_size > MAX_FILE_SIZE_BYTES:
        raise ValidationException(
            f"File size ({file_size / (1024*1024):.2f}MB) exceeds the 10MB limit per file."
        )
    if current_case_total_bytes + file_size > MAX_CASE_TOTAL_BYTES:
        raise ValidationException(
            f"Total attachment size for this case exceeds the 50MB maximum limit."
        )

    # 2. Extension check
    parts = file_name.rsplit(".", 1)
    if len(parts) < 2:
        raise ValidationException("File must have a valid extension.")
    ext = parts[1].lower().strip()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationException(
            f"Disallowed file extension '.{ext}'. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}."
        )

    # 3. Magic bytes check
    if ext in MAGIC_SIGNATURES:
        signatures = MAGIC_SIGNATURES[ext]
        if not any(file_bytes.startswith(sig) for sig in signatures):
            raise ValidationException(
                f"File content does not match the stated '.{ext}' format (magic byte mismatch)."
            )
    elif ext == "webp":
        if not (file_bytes.startswith(b"RIFF") and b"WEBP" in file_bytes[:16]):
            raise ValidationException("Invalid WebP file content.")
    elif ext in ["txt", "log"]:
        # Verify text is UTF-8 decodable and does not contain null binary bytes
        try:
            sample = file_bytes[:1024].decode("utf-8")
            if "\x00" in sample:
                raise ValidationException("Text file contains binary or executable content.")
        except UnicodeDecodeError:
            raise ValidationException("Text file must be valid UTF-8 text.")

    # Determine MIME type
    mime_map = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp",
        "gif": "image/gif",
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "txt": "text/plain",
        "log": "text/plain",
    }
    return ext, mime_map.get(ext, "application/octet-stream")
