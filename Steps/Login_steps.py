from pytest_bdd import parsers
from pytest_bdd import given, scenarios, then, when
from selenium.common.exceptions import WebDriverException

from src.pages.home_page import HomePage
from src.pages.login_page import LoginPage

scenarios("../Features/Login.feature")


def _quick_screen_state(driver) -> str:
    try:
        src = (driver.page_source or "").lower()
    except Exception:
        return "unknown"

    if "welcome back!" in src or "enter your email" in src:
        return "login"
    if "let's get started" in src or "lets get started" in src or "let\u2019s get started" in src:
        return "welcome"
    if "menu_action_setting" in src or "img_header" in src:
        return "home"
    return "unknown"


def _soft_relaunch_app(driver):
    caps = driver.capabilities
    app_package = caps.get("appium:appPackage") or caps.get("appPackage")
    if not app_package:
        return
    try:
        driver.terminate_app(app_package)
    except Exception:
        pass
    try:
        driver.activate_app(app_package)
    except Exception:
        pass


def _safe_back(driver) -> bool:
    try:
        driver.back()
        return True
    except WebDriverException:
        return False


def _ensure_login_screen_without_relaunch(driver):
    page = LoginPage(driver)
    home = HomePage(driver)

    state = _quick_screen_state(driver)
    if state == "login":
        return
    if state == "home":
        home.logout_from_menu()
        return
    if state == "welcome":
        page.navigate_to_login_if_needed()
        if page.is_login_screen_visible(timeout=4):
            return

    if page.is_invalid_alert_visible(timeout=2):
        page.dismiss_invalid_alert()

    if page.is_login_screen_visible(timeout=3):
        return

    if home.is_home_header_visible(timeout=4):
        home.logout_from_menu()
        if page.is_login_screen_visible(timeout=10):
            return

    page.navigate_to_login_if_needed()
    if page.is_login_screen_visible(timeout=6):
        return

    # Handle deep in-app pages (for example settings/detail screens).
    for _ in range(3):
        if not _safe_back(driver):
            break

        state = _quick_screen_state(driver)
        if state == "login":
            return
        if state == "welcome":
            page.navigate_to_login_if_needed()
            if page.is_login_screen_visible(timeout=4):
                return
        if state == "home":
            home.logout_from_menu()
            if page.is_login_screen_visible(timeout=6):
                return

    # Last fallback when state is unknown: soft relaunch once and navigate.
    _soft_relaunch_app(driver)
    try:
        page.navigate_to_login_if_needed()
    except WebDriverException:
        pass

    if page.is_login_screen_visible(timeout=6):
        return


@given("user is on login screen")
def user_on_login_screen(driver):
    _ensure_login_screen_without_relaunch(driver)
    page = LoginPage(driver)
    assert page.is_login_screen_visible(), "Login screen was not visible"
    page.reset_form()
    return page


@when("user logs in with valid credentials")
def valid_login(driver, env_setup, login_data):
    email = env_setup["email"]
    password = env_setup["password"]
    assert email and password, "Missing SHOPPIX_LOGIN_EMAIL or SHOPPIX_LOGIN_PASSWORD in .env"

    page = LoginPage(driver)
    page.navigate_to_login_if_needed()
    page.login_with_credentials(email=email, password=password)


@when("user logs in with invalid credentials")
def invalid_login(driver, login_data):
    invalid_user = login_data["invalid_user"]
    page = LoginPage(driver)
    page.navigate_to_login_if_needed()
    page.login_with_credentials(email=invalid_user["email"], password=invalid_user["password"])


@when("user dismisses invalid credential alert")
def dismiss_invalid_alert(driver):
    page = LoginPage(driver)
    page.dismiss_invalid_alert()


@then("invalid credential alert should be visible")
def invalid_alert_visible(driver, login_data):
    expected = login_data["expected"]
    title, message = LoginPage(driver).get_invalid_alert(expected["invalid_messages"])
    assert title == expected["invalid_title"], "Invalid alert title did not match"
    assert message in expected["invalid_messages"], "Invalid alert message did not match allowed variants"


@then("app home header should be visible")
def app_home_header_visible(driver):
    assert HomePage(driver).is_home_header_visible(), "Home header was not visible after login"


@when("user logs out from home menu")
def user_logs_out_from_home_menu(driver):
    HomePage(driver).logout_from_menu()


@then("user should be on login screen")
def user_should_be_on_login_screen(driver):
    assert LoginPage(driver).is_login_screen_visible(timeout=20), "Login screen was not visible after sign out"


def _resolve_credential_token(raw_value: str, env_setup: dict) -> str:
    if raw_value == "VALID_EMAIL":
        return env_setup["email"]
    if raw_value == "VALID_PASSWORD":
        return env_setup["password"]
    if raw_value == "SPACED_INVALID_EMAIL":
        return "  invalid.user@example.com  "
    return raw_value


@when(parsers.re(r'^user enters email "(?P<email_input>.*)" and password "(?P<password_input>.*)"$'))
def user_enters_credentials(driver, env_setup, email_input: str, password_input: str):
    page = LoginPage(driver)
    page.navigate_to_login_if_needed()
    email = _resolve_credential_token(email_input, env_setup)
    password = _resolve_credential_token(password_input, env_setup)
    page.enter_email(email)
    page.enter_password(password)


@when("user taps login button")
def user_taps_login_button(driver):
    LoginPage(driver).tap_login()


@then("email and password placeholders should be visible")
def placeholders_should_be_visible(driver):
    page = LoginPage(driver)
    assert page.are_field_labels_visible(), "Email/Password labels were not visible"
    assert page.is_email_field_ready(), "Email field had neither placeholder nor prefilled value"
    assert page.is_password_placeholder_visible(), "Password placeholder was not visible"


@then("login button should be disabled")
def login_button_should_be_disabled(driver):
    assert not LoginPage(driver).is_login_button_enabled(), "Login button was enabled unexpectedly"


@then("authentication should fail safely")
def authentication_should_fail_safely(driver, login_data):
    page = LoginPage(driver)

    # Failure is valid when app stays on login screen with no successful home navigation.
    if HomePage(driver).is_home_header_visible(timeout=4):
        raise AssertionError("Authentication unexpectedly navigated to Home")

    if page.is_invalid_alert_visible(timeout=4):
        title, message = page.get_invalid_alert(login_data["expected"]["invalid_messages"])
        assert title == login_data["expected"]["invalid_title"], "Invalid alert title did not match"
        assert message in login_data["expected"]["invalid_messages"], "Invalid alert message did not match allowed variants"
        page.dismiss_invalid_alert()
        return

    assert page.is_login_screen_visible(timeout=6), "Login screen was not visible after failed authentication"
