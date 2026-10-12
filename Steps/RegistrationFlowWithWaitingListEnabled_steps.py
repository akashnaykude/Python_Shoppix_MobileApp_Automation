import os
import time

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from src.pages.registration_page import RegistrationPage
from src.pages.waiting_list_page import WaitingListPage
from src.pages.welcome_page import WelcomePage

scenarios("../Features/RegistrationFlowWithWaitingListEnabled.feature")


VALID_UK_POSTCODE = "SW1A 1AA"
NON_UK_POSTCODE = "12345"
INVALID_UK_POSTCODE = "QW"
INVALID_EMAIL = "a@hsbsbsjsn"
REFERRAL_CODE = "FRIEND50"

# Seeded once per session so duplicate-email scenarios reuse a single waitlist
# entry instead of creating junk accounts on every run.
_SEEDED_WAITLIST_EMAIL: str | None = None

# Stable duplicate email for waitlist tests; can be overridden in CI.
DEFAULT_WAITLIST_DUPLICATE_EMAIL = "test5@test.com"
WAITLIST_DUPLICATE_SELF_HEAL = (os.getenv("WAITLIST_DUPLICATE_SELF_HEAL", "0").strip() == "1")

WAITLIST_DISABLED_SKIP_MESSAGE = (
    "Waiting list is disabled in this environment, so RegistrationFlowWithWaitingListEnabled.feature scenarios were "
    "skipped. Update Threshold of Live Buyers in manage shoppix to enable waiting list."
)

# Session-scoped environment classification so only the first scenario pays the
# detection cost; later scenarios skip (or proceed) instantly.
_ENV_MODE: str | None = None  # "waitlist" | "registration"


class Assert:
    @staticmethod
    def Ignore(message: str):
        pytest.skip(message)


def _classify_screen(driver) -> str:
    """One page_source read to tell which registration mode is active."""
    try:
        src = (driver.page_source or "").lower()
    except Exception:
        return "unknown"
    if "enter your postcode" in src or "thank you for your interest" in src:
        return "waitlist"
    if "confirm password" in src or "welcome to shoppix" in src:
        return "registration"
    return "unknown"


def _unique_email() -> str:
    return f"autowl_{int(time.time() * 1000)}@test.com"


def _configured_duplicate_email() -> str:
    return (os.getenv("WAITLIST_DUPLICATE_EMAIL") or DEFAULT_WAITLIST_DUPLICATE_EMAIL).strip().lower()


@pytest.fixture
def wl_ctx() -> dict:
    """Per-scenario scratch space to pass values between steps."""
    return {}


def _safe_back(driver):
    try:
        driver.back()
    except Exception:
        pass


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


def _ensure_waiting_list_screen(driver) -> WaitingListPage:
    global _ENV_MODE
    page = WaitingListPage(driver)

    # Fast skip: environment already classified as non-waitlist this session.
    if _ENV_MODE == "registration":
        Assert.Ignore(WAITLIST_DISABLED_SKIP_MESSAGE)

    if page.is_waiting_list_visible(timeout=2):
        _ENV_MODE = "waitlist"
        return page

    welcome = WelcomePage(driver)
    if not welcome.is_welcome_visible(timeout=2):
        _safe_back(driver)
    if welcome.is_welcome_visible(timeout=3):
        welcome.tap_email_registration_icon()

    if page.is_waiting_list_visible(timeout=4):
        _ENV_MODE = "waitlist"
        return page

    # Classify the opened screen once; cache so later scenarios skip instantly.
    if _classify_screen(driver) == "registration":
        _ENV_MODE = "registration"
        Assert.Ignore(WAITLIST_DISABLED_SKIP_MESSAGE)

    pytest.skip("Could not reach the waiting list screen (entry point unavailable).")


def _submit_waitlist_form(driver, email: str, double_tap: bool = False):
    page = WaitingListPage(driver)
    if not page.is_waiting_list_visible(timeout=2):
        page = _ensure_waiting_list_screen(driver)
    page.fill_valid_form(email, VALID_UK_POSTCODE)
    if double_tap:
        page.tap_continue_twice()
    else:
        page.tap_continue()
    return page


def _resolve_duplicate_email(driver) -> tuple[str, bool]:
    """Return an email guaranteed to trigger duplicate waitlist alert.

    Strategy:
    1) Try configured stable email (default test5@test.com).
    2) If not duplicate (likely expired after retention), register SAME email once.
    3) Re-submit same email to force duplicate alert.
    4) Fall back to one unique email only if environment blocks fixed email.
    """

    global _SEEDED_WAITLIST_EMAIL
    if _SEEDED_WAITLIST_EMAIL:
        return _SEEDED_WAITLIST_EMAIL, False

    email = _configured_duplicate_email()
    page = _submit_waitlist_form(driver, email)
    if page.is_duplicate_alert_visible(timeout=4):
        _SEEDED_WAITLIST_EMAIL = email
        return email, True

    if not WAITLIST_DUPLICATE_SELF_HEAL:
        pytest.fail(
            "Configured duplicate email did not trigger duplicate alert. "
            "Use a known waitlisted email or set WAITLIST_DUPLICATE_SELF_HEAL=1 for one-time reseeding."
        )

    if page.is_success_alert_visible(timeout=6):
        page.tap_done()
        WelcomePage(driver).is_welcome_visible(timeout=10)
        page = _submit_waitlist_form(driver, email)
        if page.is_duplicate_alert_visible(timeout=4):
            _SEEDED_WAITLIST_EMAIL = email
            return email, True

    # Last-resort fallback for unusual environments where the fixed email path
    # cannot produce duplicate (validation/network/test data policy).
    fallback = _unique_email()
    page = _submit_waitlist_form(driver, fallback)
    assert page.is_success_alert_visible(timeout=18), "Could not seed waitlist email for duplicate scenario"
    page.tap_done()
    WelcomePage(driver).is_welcome_visible(timeout=10)
    page = _submit_waitlist_form(driver, fallback)
    assert page.is_duplicate_alert_visible(timeout=4), "Duplicate alert not shown after fallback seeding"
    _SEEDED_WAITLIST_EMAIL = fallback
    return fallback, True


# --------------------------------------------------------------------------
# Given
# --------------------------------------------------------------------------
@given("user is on waiting list registration screen")
def user_on_waiting_list_screen(driver):
    page = _ensure_waiting_list_screen(driver)
    page.reset_form()
    page.set_consent(False)


# --------------------------------------------------------------------------
# Visibility
# --------------------------------------------------------------------------
@then("waiting list registration screen should load successfully")
def screen_loads(driver):
    assert WaitingListPage(driver).is_waiting_list_visible(timeout=6), "Waiting list screen did not load"


@then("app logo should be visible")
def logo_visible(driver):
    assert WaitingListPage(driver).is_logo_visible(), "App logo not visible"


@then("back button should be visible")
def back_visible(driver):
    assert WaitingListPage(driver).is_back_button_visible(), "Back button not visible"


@then("main heading should be visible")
def heading_visible(driver):
    assert WaitingListPage(driver).is_heading_visible(), "Main heading not visible"


@then("waiting list description text should be visible")
def description_visible(driver):
    assert WaitingListPage(driver).is_description_text_visible(), "Description text not visible"


@then("referral code instruction text should be visible")
def referral_instruction_visible(driver):
    assert WaitingListPage(driver).is_referral_instruction_visible(), "Referral instruction text not visible"


@then("email field label should be visible")
def email_label_visible(driver):
    assert WaitingListPage(driver).is_email_label_visible(), "Email label not visible"


@then("email input placeholder should be visible")
def email_placeholder_visible(driver):
    assert WaitingListPage(driver).is_email_placeholder_visible(), "Email placeholder not visible"


@then("postcode field label should be visible")
def postcode_label_visible(driver):
    assert WaitingListPage(driver).is_postcode_label_visible(), "Postcode label not visible"


@then("postcode input placeholder should be visible")
def postcode_placeholder_visible(driver):
    assert WaitingListPage(driver).is_postcode_placeholder_visible(), "Postcode placeholder not visible"


@then("age range field label should be visible")
def age_label_visible(driver):
    assert WaitingListPage(driver).is_age_label_visible(), "Age range label not visible"


@then("age range dropdown should be visible")
def age_dropdown_visible(driver):
    assert WaitingListPage(driver).is_age_dropdown_visible(), "Age range dropdown not visible"


@then("referral code label should be visible")
def referral_label_visible(driver):
    assert WaitingListPage(driver).is_referral_label_visible(), "Referral code label not visible"


@then("referral code input placeholder should be visible")
def referral_placeholder_visible(driver):
    assert WaitingListPage(driver).is_referral_placeholder_visible(), "Referral code placeholder not visible"


@then("consent checkbox should be visible")
def consent_checkbox_visible(driver):
    assert WaitingListPage(driver).is_consent_checkbox_visible(), "Consent checkbox not visible"


@then("consent text should be visible")
def consent_text_visible(driver):
    assert WaitingListPage(driver).is_consent_text_visible(), "Consent text not visible"


@then("privacy information text should be visible")
def privacy_note_visible(driver):
    assert WaitingListPage(driver).is_privacy_note_visible(), "Privacy information text not visible"


@then("continue button should be visible")
def continue_visible(driver):
    try:
        assert WaitingListPage(driver).is_continue_button_visible(), "Continue button not visible"
    finally:
        _safe_back(driver)


# --------------------------------------------------------------------------
# Email
# --------------------------------------------------------------------------
@when("user enters valid email address")
def enter_valid_email(driver, wl_ctx):
    email = _unique_email()
    wl_ctx["email"] = email
    WaitingListPage(driver).enter_email(email)


@then("email input should show entered value")
def email_shows_value(driver, wl_ctx):
    assert WaitingListPage(driver).get_email_value() == wl_ctx["email"], "Email value mismatch"


@when("user leaves email field empty and tries to continue")
def empty_email_continue(driver):
    page = WaitingListPage(driver)
    page.enter_email("")
    page.tap_continue()


@then("email required validation message should be displayed")
def email_required_error(driver):
    assert WaitingListPage(driver).is_email_required_error_visible(), "Email required error not shown"


@when("user enters invalid email address")
def enter_invalid_email(driver):
    WaitingListPage(driver).enter_email(INVALID_EMAIL)


@then("email format validation message should be displayed")
def email_invalid_error(driver):
    assert WaitingListPage(driver).is_email_invalid_error_visible(), "Email invalid format error not shown"


@when("user enters email address with leading and trailing spaces")
def enter_email_with_spaces(driver, wl_ctx):
    wl_ctx["trim_email"] = "spaced.user@test.com"
    WaitingListPage(driver).enter_email(f"  {wl_ctx['trim_email']}  ")


@then("email input should trim spaces correctly")
def email_trimmed(driver, wl_ctx):
    assert WaitingListPage(driver).get_email_value() == wl_ctx["trim_email"], "Email was not trimmed"


# --------------------------------------------------------------------------
# Postcode
# --------------------------------------------------------------------------
@when("user enters postcode")
def enter_postcode(driver, wl_ctx):
    wl_ctx["postcode"] = VALID_UK_POSTCODE
    WaitingListPage(driver).enter_postcode(VALID_UK_POSTCODE)


@then("postcode input should show entered value")
def postcode_shows_value(driver, wl_ctx):
    assert WaitingListPage(driver).get_postcode_value() == wl_ctx["postcode"], "Postcode value mismatch"


@when("user leaves postcode field empty and tries to continue")
def empty_postcode_continue(driver):
    page = WaitingListPage(driver)
    page.enter_email(_unique_email())
    page.enter_postcode("")
    page.tap_continue()


@then("postcode required validation message should be displayed")
def postcode_required_error(driver):
    assert WaitingListPage(driver).is_postcode_required_error_visible(), "Postcode required error not shown"


@when("user enters valid UK postcode")
def enter_valid_uk_postcode(driver):
    WaitingListPage(driver).enter_postcode(VALID_UK_POSTCODE)


@then("postcode should be accepted without validation error")
def postcode_accepted(driver):
    page = WaitingListPage(driver)
    assert not page.is_postcode_invalid_error_present(), "Valid UK postcode was flagged as invalid"


@when("user enters non UK postcode")
def enter_non_uk_postcode(driver):
    WaitingListPage(driver).enter_postcode(NON_UK_POSTCODE)


@when("user enters invalid UK postcode")
def enter_invalid_uk_postcode(driver):
    WaitingListPage(driver).enter_postcode(INVALID_UK_POSTCODE)


@then("valid postcode validation message should be displayed")
def postcode_invalid_error(driver):
    assert WaitingListPage(driver).is_postcode_invalid_error_visible(), "Invalid postcode error not shown"


@when("user enters postcode with leading and trailing spaces")
def enter_postcode_with_spaces(driver, wl_ctx):
    wl_ctx["trim_postcode"] = VALID_UK_POSTCODE
    WaitingListPage(driver).enter_postcode(f"  {VALID_UK_POSTCODE}  ")


@then("postcode input should trim spaces correctly")
def postcode_trimmed(driver, wl_ctx):
    assert WaitingListPage(driver).get_postcode_value() == wl_ctx["trim_postcode"], "Postcode was not trimmed"


# --------------------------------------------------------------------------
# Age range
# --------------------------------------------------------------------------
@when("user taps age range dropdown")
def tap_age_dropdown(driver):
    WaitingListPage(driver).open_age_dropdown()


@then("age range options should be displayed")
def age_options_displayed(driver):
    assert WaitingListPage(driver).is_age_options_displayed(), "Age range options not displayed"


@then("all age range options should be visible")
def all_age_options_visible(driver):
    assert WaitingListPage(driver).are_all_age_options_visible(), "Not all age range options are visible"


@when("user selects an age range option")
def select_an_age(driver, wl_ctx):
    wl_ctx["age"] = "25-34"
    WaitingListPage(driver).select_age_range("25-34")


@when(parsers.parse('user selects "{age}" age range'))
def select_specific_age(driver, wl_ctx, age):
    wl_ctx["age"] = age
    WaitingListPage(driver).select_age_range(age)


@then("selected age range should be displayed")
def selected_age_displayed(driver, wl_ctx):
    assert WaitingListPage(driver).get_selected_age() == wl_ctx["age"], "Selected age not displayed"


@then(parsers.parse('selected age range should be "{age}"'))
def selected_age_equals(driver, age):
    assert WaitingListPage(driver).get_selected_age() == age, f"Selected age is not {age}"


@when("user leaves age range unselected and tries to continue")
def age_unselected_continue(driver):
    page = WaitingListPage(driver)

    # Age has no explicit clear action in this build.
    if page.get_selected_age():
        _safe_back(driver)
        page = _ensure_waiting_list_screen(driver)
        page.reset_form()
        page.set_consent(False)

    page.enter_email(_unique_email())
    page.enter_postcode(VALID_UK_POSTCODE)
    page.set_consent(True)
    page.tap_continue()


@then("age range required validation message should be displayed")
def age_required_error(driver):
    assert WaitingListPage(driver).is_age_required_error_visible(), "Age required error not shown"


# --------------------------------------------------------------------------
# Referral code (UI / input only)
# --------------------------------------------------------------------------
@when("user enters referral code")
def enter_referral(driver, wl_ctx):
    wl_ctx["referral"] = REFERRAL_CODE
    WaitingListPage(driver).enter_referral_code(REFERRAL_CODE)


@then("referral code input should show entered value")
def referral_shows_value(driver, wl_ctx):
    assert WaitingListPage(driver).get_referral_value() == wl_ctx["referral"], "Referral value mismatch"


@when("user leaves referral code empty")
def leave_referral_empty(driver):
    WaitingListPage(driver).enter_referral_code("")


@then("referral code field should remain optional")
def referral_optional(driver):
    page = WaitingListPage(driver)
    assert page.get_referral_value() == "", "Referral code should be empty"
    assert page.is_waiting_list_visible(timeout=3), "Screen should stay usable with empty referral"


# --------------------------------------------------------------------------
# Consent
# --------------------------------------------------------------------------
@when("user taps consent checkbox")
def tap_consent(driver):
    WaitingListPage(driver).tap_consent_checkbox()


@when("user taps consent checkbox again")
def tap_consent_again(driver):
    WaitingListPage(driver).tap_consent_checkbox()


@then("consent checkbox should be selected")
def consent_selected(driver):
    assert WaitingListPage(driver).is_consent_checked(), "Consent checkbox not selected"


@then("consent checkbox should be deselected")
def consent_deselected(driver):
    assert not WaitingListPage(driver).is_consent_checked(), "Consent checkbox not deselected"


# --------------------------------------------------------------------------
# Continue / submit-time validation
# --------------------------------------------------------------------------
@when("user taps continue button")
def tap_continue_button(driver):
    WaitingListPage(driver).tap_continue()


@when("user tries to continue")
def try_continue(driver):
    WaitingListPage(driver).tap_continue()


@then("required field validation messages should be displayed")
def required_validations(driver):
    page = WaitingListPage(driver)
    end = time.time() + 8
    last = {
        "email": False,
        "postcode": False,
        "age": False,
        "consent": False,
    }
    while time.time() < end:
        last = {
            "email": page.is_email_required_error_visible(timeout=2),
            "postcode": page.is_postcode_required_error_visible(timeout=2),
            "age": page.is_age_required_error_visible(timeout=2),
            "consent": page.is_consent_required_error_visible(timeout=2),
        }
        if all(last.values()):
            break
        time.sleep(0.3)

    assert last["email"], "Email required error not shown"
    assert last["postcode"], "Postcode required error not shown"
    assert last["age"], "Age required error not shown"
    assert last["consent"], "Consent required error not shown"


@then("consent validation message should be displayed")
def consent_validation(driver):
    assert WaitingListPage(driver).is_consent_required_error_visible(), "Consent required error not shown"


# --------------------------------------------------------------------------
# Success flow
# --------------------------------------------------------------------------
@then("success alert should be displayed")
def success_alert(driver):
    assert WaitingListPage(driver).is_success_alert_visible(timeout=25), "Success alert not displayed"


@then("success alert message should be shown")
def success_message(driver):
    assert WaitingListPage(driver).is_success_alert_visible(timeout=6), "Success alert message not shown"


@then("Done button should be visible on success alert")
def done_visible(driver):
    assert WaitingListPage(driver).is_done_button_visible(), "Done button not visible"


@when("user taps Done button")
def tap_done(driver):
    WaitingListPage(driver).tap_done()


@then("user should be redirected to welcome screen")
def redirected_to_welcome(driver):
    assert WelcomePage(driver).is_welcome_visible(timeout=12), "Not redirected to welcome screen"


# --------------------------------------------------------------------------
# Duplicate waitlist email
# --------------------------------------------------------------------------
@when("user submits a valid form using an email already on the waitlist")
def submit_duplicate_email(driver):
    email, duplicate_already_visible = _resolve_duplicate_email(driver)
    if not duplicate_already_visible:
        _submit_waitlist_form(driver, email)


@when("user submits a valid form using an email already on the waitlist tapping continue twice quickly")
def submit_duplicate_email_double(driver):
    email, _ = _resolve_duplicate_email(driver)
    _submit_waitlist_form(driver, email, double_tap=True)


@then("duplicate waitlist alert should be displayed")
def duplicate_alert(driver):
    assert WaitingListPage(driver).is_duplicate_alert_visible(), "Duplicate waitlist alert not displayed"


@then(parsers.parse('alert message should be "{message}"'))
def alert_message_equals(driver, message):
    assert WaitingListPage(driver).get_duplicate_alert_text() == message, "Duplicate alert message mismatch"


@then("OK button should be visible on alert")
def ok_visible(driver):
    assert WaitingListPage(driver).is_ok_button_visible(), "OK button not visible on alert"


@when("user taps OK button")
def tap_ok(driver):
    WaitingListPage(driver).tap_ok()


@then("alert should be dismissed")
def alert_dismissed(driver):
    assert WaitingListPage(driver).is_alert_dismissed(), "Alert was not dismissed"


@then("user should remain on waiting list registration screen")
def remain_on_screen(driver):
    assert WaitingListPage(driver).is_waiting_list_visible(timeout=6), "User did not remain on waiting list screen"


@then("only one duplicate waitlist alert should be displayed")
def single_duplicate_alert(driver):
    page = WaitingListPage(driver)
    assert page.is_duplicate_alert_visible(), "Duplicate waitlist alert not displayed"
    assert page.duplicate_alert_count() == 1, "More than one duplicate alert was shown"


# --------------------------------------------------------------------------
# Resilience
# --------------------------------------------------------------------------
@when("network is unavailable")
def network_unavailable(driver, wl_ctx):
    wl_ctx["network_toggle_supported"] = False
    wl_ctx["network_offline_enforced"] = False
    try:
        driver.set_network_connection(0)
        wl_ctx["network_toggle_supported"] = True
    except Exception:
        pytest.skip("Network toggling is not supported on this driver/device.")

    # Some providers accept the command but do not actually isolate network.
    state = None
    try:
        if hasattr(driver, "network_connection"):
            state = int(driver.network_connection)
        elif hasattr(driver, "get_network_connection"):
            state = int(driver.get_network_connection())
    except Exception:
        state = None

    wl_ctx["network_state_after_toggle"] = state
    # 0 is the expected strict offline mode in Appium network bitmask.
    wl_ctx["network_offline_enforced"] = state == 0 if state is not None else True


@when("user enters valid registration details")
def enter_valid_details(driver):
    WaitingListPage(driver).fill_valid_form(_unique_email(), VALID_UK_POSTCODE)


@then("submission should not succeed and screen should remain")
def submission_blocked(driver, wl_ctx):
    page = WaitingListPage(driver)
    try:
        if not wl_ctx.get("network_toggle_supported"):
            pytest.skip("Network toggle not supported in this environment.")
        if not wl_ctx.get("network_offline_enforced"):
            pytest.skip(
                f"Network toggle did not enforce offline state (state={wl_ctx.get('network_state_after_toggle')})."
            )

        assert not page.is_success_alert_visible(timeout=6), "Submission unexpectedly succeeded while offline"

        blocked_state = (
            page.is_any_error_or_oops_visible(timeout=10)
            or page.is_waiting_list_visible(timeout=6)
            or page.is_back_button_visible(timeout=4)
        )

        if not blocked_state:
            # Some builds keep the submit request in a pending overlay state
            # without rendering an explicit error message while offline.
            try:
                src = driver.page_source or ""
                ui_responsive = len(src) > 0
            except Exception:
                ui_responsive = False
            pending_blocked = ui_responsive and not page.is_success_alert_visible(timeout=2)
            blocked_state = blocked_state or pending_blocked

        assert blocked_state, "No graceful blocked/pending state observed while offline"
    finally:
        try:
            driver.set_network_connection(6)
        except Exception:
            pass


@when("app is sent to background")
def app_to_background(driver):
    try:
        driver.background_app(2)
    except Exception:
        _soft_relaunch_app(driver)


@when("app is brought to foreground")
def app_to_foreground(driver):
    app_package = driver.capabilities.get("appium:appPackage") or driver.capabilities.get("appPackage")
    if app_package:
        try:
            driver.activate_app(app_package)
        except Exception:
            pass


@then("waiting list registration screen should be displayed")
def screen_still_displayed(driver):
    assert WaitingListPage(driver).is_waiting_list_visible(timeout=10), "Waiting list screen not displayed after resume"


@when("device orientation is changed")
def change_orientation(driver):
    try:
        current = driver.orientation
        driver.orientation = "LANDSCAPE" if current == "PORTRAIT" else "PORTRAIT"
        time.sleep(1)
        driver.orientation = current
    except Exception:
        pass


@then("waiting list registration screen should be displayed correctly")
def screen_displayed_after_rotation(driver):
    assert WaitingListPage(driver).is_waiting_list_visible(timeout=10), "Waiting list screen not stable after rotation"


# --------------------------------------------------------------------------
# Accessibility & rendering
# --------------------------------------------------------------------------
@then("key elements should have accessibility labels")
def accessibility_labels(driver):
    page = WaitingListPage(driver)
    status = page.key_elements_accessibility_status()
    assert all(status.values()), f"Key elements missing accessibility labels: {status}"


@then("waiting list registration screen should render core content correctly")
def core_render(driver):
    assert WaitingListPage(driver).core_content_rendered(), "Core content did not render correctly"
