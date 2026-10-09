import os
from pathlib import Path
from typing import Any

import allure
import pytest
from dotenv import load_dotenv

from src.core.activity_resolver import resolve_launch_activity
from src.core.apk_resolver import resolve_latest_apk
from src.core.config_loader import load_json
from src.core.driver_factory import create_android_driver


# Collection order for end-to-end flow execution.
ORDERED_STEP_KEYWORDS: list[tuple[str, int]] = [
    ("Welcome_steps.py", 10),
    ("RegistrationFlowWithWaitingListEnabled", 20),
    ("Registration_steps.py", 30),
    ("Login_steps.py", 40),
    ("Home_steps.py", 50),
]


@pytest.fixture(scope="session")
def env_setup():
    load_dotenv()
    return {
        "email": os.getenv("SHOPPIX_LOGIN_EMAIL", ""),
        "password": os.getenv("SHOPPIX_LOGIN_PASSWORD", ""),
    }


@pytest.fixture(scope="session")
def run_profile_path() -> Path:
    return Path("configs/profiles/stage.android.local.json")


@pytest.fixture(scope="session")
def run_profile(run_profile_path: Path) -> dict:
    profile = load_json(str(run_profile_path))
    apk_cfg = profile["apk"]
    resolved_apk = resolve_latest_apk(
        base_folder=apk_cfg["base_folder"],
        apk_name=apk_cfg["fixed_apk_name"],
    )
    capabilities = profile["capabilities"]
    capabilities["appium:app"] = str(resolved_apk)

    app_package = capabilities.get("appium:appPackage")
    udid = capabilities.get("appium:udid")
    if app_package and udid:
        resolved_activity = resolve_launch_activity(udid=udid, app_package=app_package)
        if resolved_activity:
            capabilities["appium:appActivity"] = resolved_activity

    capabilities.setdefault("appium:appWaitActivity", "*")
    capabilities.setdefault("appium:appWaitDuration", 20000)
    return profile


@pytest.fixture(scope="session")
def driver(run_profile: dict):
    drv = create_android_driver(
        server_url=run_profile["appium_server"],
        capabilities=run_profile["capabilities"],
    )
    app_package = run_profile["capabilities"].get("appium:appPackage")
    if app_package:
        try:
            drv.activate_app(app_package)
        except Exception:
            # Session may already be on target app. Keep test flow resilient.
            pass
    yield drv
    drv.quit()


@pytest.fixture(scope="session")
def login_data() -> dict[str, Any]:
    return load_json("Data/Login/stage_login_data.json")


def _attach_failure_artifacts(driver_obj, test_name: str):
    Path("artifacts/screenshots").mkdir(parents=True, exist_ok=True)
    screenshot_path = Path("artifacts/screenshots") / f"{test_name}.png"
    page_source_path = Path("artifacts/screenshots") / f"{test_name}.xml"

    # Driver can be half-crashed on failure; never break test reporting hook.
    try:
        driver_obj.save_screenshot(str(screenshot_path))
        allure.attach.file(str(screenshot_path), name=f"{test_name}_screenshot", attachment_type=allure.attachment_type.PNG)
    except Exception:
        pass

    try:
        page_source_path.write_text(driver_obj.page_source, encoding="utf-8")
        allure.attach.file(str(page_source_path), name=f"{test_name}_page_source", attachment_type=allure.attachment_type.XML)
    except Exception:
        pass


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when not in {"setup", "call"} or report.passed:
        return

    driver_obj = item.funcargs.get("driver")
    if not driver_obj:
        return

    safe_name = item.nodeid.replace("::", "_").replace("/", "_").replace("\\", "_")
    _attach_failure_artifacts(driver_obj, safe_name)


def _item_execution_rank(nodeid: str) -> tuple[int, str]:
    for keyword, rank in ORDERED_STEP_KEYWORDS:
        if keyword in nodeid:
            return rank, nodeid
    return 1000, nodeid


def pytest_collection_modifyitems(session, config, items):
    items.sort(key=lambda item: _item_execution_rank(item.nodeid))
