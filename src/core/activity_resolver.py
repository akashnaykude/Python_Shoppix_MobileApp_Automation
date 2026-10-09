import subprocess


def resolve_launch_activity(udid: str, app_package: str) -> str | None:
    """Resolve current launchable activity for a package from connected device."""
    cmd = [
        "adb",
        "-s",
        udid,
        "shell",
        "cmd",
        "package",
        "resolve-activity",
        "--brief",
        app_package,
    ]
    try:
        output = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)
    except Exception:
        return None

    lines = [line.strip() for line in output.splitlines() if line.strip()]
    for line in reversed(lines):
        if "/" in line and line.startswith(app_package):
            _, activity = line.split("/", 1)
            return activity
    return None