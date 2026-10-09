from pathlib import Path


def resolve_latest_apk(base_folder: str, apk_name: str) -> Path:
    """Return the latest modified subfolder APK path."""
    base = Path(base_folder)
    if not base.exists():
        raise FileNotFoundError(f"APK base folder not found: {base}")

    subfolders = [p for p in base.iterdir() if p.is_dir()]
    if not subfolders:
        raise FileNotFoundError(f"No dated folders found under: {base}")

    latest = max(subfolders, key=lambda p: p.stat().st_mtime)
    apk_path = latest / apk_name
    if not apk_path.exists():
        raise FileNotFoundError(f"APK not found in latest folder: {apk_path}")

    return apk_path
