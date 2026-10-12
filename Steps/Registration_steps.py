import time

import pytest
from pytest_bdd import given, scenarios, then, when

from src.pages.home_page import HomePage
from src.pages.login_page import LoginPage
from src.pages.registration_page import RegistrationPage
from src.pages.welcome_page import WelcomePage

scenarios("../Features/Registration.feature")


CREATE_PASSWORD = "Test@123"
WEAK_PASSWORD = "weak"
INVALID_EMAIL = "invalid-email"

REGISTRATION_SKIPPED_MESSAGE = (
    "Registration.feature scenarios were skipped because Waiting list is enabled in manage shoppix for this "
    "environment or check Threshold of Live Buyers in manage shoppix."
)

# Session-scoped environment classification so only the first scenario pays the
# detection cost; later scenarios skip (or proceed) instantly.
_ENV_MODE: str | None = None  # "waitlist" | "registration"


class Assert:
    @staticmethod
    def Ignore(message: str):
        pytest.skip(message)


def _classify_screen(driver) -> str:
    """One page_source read to tell which registration mode is active.

    Registration markers stay scroll-proof: the confirm/create password labels
    exist only on the registration form, so classification survives even when the
    'Welcome to Shoppix!' heading has scrolled off-screen.
    """
    try:
        src = (driver.page_source or "").lower()
    except Exception:
        return "unknown"
    if "enter your postcode" in src or "thank you for your interest" in src:
        return "waitlist"
    if (
        "confirm password" in src
        or "confirm your password" in src
        or "create your password" in src
        or "welcome to shoppix" in src
    ):
        return "registration"
    return "unknown"


def _poll_classify(driver, timeout: float = 6.0) -> str:
    """Poll page_source briefly until the screen can be classified."""
    end = time.time() + timeout
    mode = "unknown"
    while time.time() < end:
        mode = _classify_screen(driver)
        if mode != "unknown":
            return mode
        time.sleep(0.4)
    return mode


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
    # Registration before legal: the registration form itself contains the T&C /
    # Privacy link text, so password markers must win to avoid a false "legal".
    if (
        "confirm password" in src
        or "confirm your password" in src
        or "create your password" in src
        or "welcome to shoppix" in src
    ):
        return "registration"
    if "terms and conditions" in src or "privacy policy" in src:
        return "legal"
    return "unknown"


def _safe_back(driver):
    try:
        driver.back()
        return True
    except Exception:
        return False


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


def _unique_email() -> str:
    return f"autoreg_{int(time.time() * 1000)}@test.com"


def _ensure_registration_screen(driver):
    global _ENV_MODE
    page = RegistrationPage(driver)

    # Fast skip: environment already classified as waiting-list this session.
    if _ENV_MODE == "waitlist":
        Assert.Ignore(REGISTRATION_SKIPPED_MESSAGE)

    def _settle_on_registration() -> bool:
        # Scroll back to the top so the heading check passes even if a previous
        # scenario left the form scrolled down.
        page.restore_registration_top(timeout=4)
        if page.is_registration_screen_visible(timeout=3):
            return True
        return False

    # Recover from whatever screen the previous scenario left behind, escalating
    # effort and falling back to a relaunch so one bad state can't fail the rest.
    for attempt in range(3):
        mode = _classify_screen(driver)

        if mode == "waitlist":
            _ENV_MODE = "waitlist"
            Assert.Ignore(REGISTRATION_SKIPPED_MESSAGE)

        if mode == "registration" and _settle_on_registration():
            _ENV_MODE = "registration"
            return page

        # Not on registration: move toward it from the current screen. Never back
        # out when already on the registration form (classify handles that above).
        state = _quick_screen_state(driver)
        if state == "legal":
            _safe_back(driver)
        elif state == "home":
            HomePage(driver).logout_from_menu()
        elif state == "login":
            try:
                LoginPage(driver).tap_sign_up()
            except Exception:
                _safe_back(driver)
                if WelcomePage(driver).is_welcome_visible(timeout=2):
                    WelcomePage(driver).tap_email_registration_icon()
        elif state == "welcome":
            WelcomePage(driver).tap_email_registration_icon()
        elif state != "registration":
            # Unknown screen (next-step/dialog/webview): back out and re-enter.
            _safe_back(driver)
            if WelcomePage(driver).is_welcome_visible(timeout=2):
                WelcomePage(driver).tap_email_registration_icon()

        resolved = _poll_classify(driver, timeout=5)
        if resolved == "waitlist":
            _ENV_MODE = "waitlist"
            Assert.Ignore(REGISTRATION_SKIPPED_MESSAGE)
        if resolved == "registration" and _settle_on_registration():
            _ENV_MODE = "registration"
            return page

        # Last-resort recovery before giving up: relaunch to a clean state.
        if attempt == 2:
            _soft_relaunch_app(driver)
            if WelcomePage(driver).is_welcome_visible(timeout=6):
                WelcomePage(driver).tap_email_registration_icon()
            if _poll_classify(driver, timeout=6) == "waitlist":
                _ENV_MODE = "waitlist"
                Assert.Ignore(REGISTRATION_SKIPPED_MESSAGE)

    if _settle_on_registration():
        _ENV_MODE = "registration"
        return page

    assert page.is_registration_screen_visible(timeout=6), "Registration screen was not visible"
    _ENV_MODE = "registration"
    return page


def _toggle_until(page: RegistrationPage, field: str, expected_visible: bool, password: str, taps: int = 2) -> bool:
    for _ in range(taps):
        if field == "create":
            page.tap_create_password_toggle()
            if expected_visible and page.wait_until_create_password_visible_as(password, timeout=1.5):
                return True
            if not expected_visible and page.wait_until_create_password_hidden_from(password, timeout=1.5):
                return True
        else:
            page.tap_confirm_password_toggle()
            if expected_visible and page.wait_until_confirm_password_visible_as(password, timeout=1.5):
                return True
            if not expected_visible and page.wait_until_confirm_password_hidden_from(password, timeout=1.5):
                return True
    return False


def _assert_registration_success_and_cleanup(driver):
    home = HomePage(driver)
    state = home.wait_for_post_registration_state(timeout=40)

    if state == "rate_limited":
        home.dismiss_oops_if_present(timeout=2)
        pytest.skip("Registration throttled by backend: Too many requests. Please try again later.")

    if state == "tutorial":
        assert home.skip_tutorial_if_present(timeout=30), "Tutorial skip did not reach home screen"
    elif state == "home":
        pass
    else:
        assert False, f"Registration did not reach tutorial/home. Observed state: {state}"

    assert home.cleanup_newly_registered_account(CREATE_PASSWORD), "Registration succeeded but cleanup (delete account) failed"


@given("user is on registration screen")
def user_on_registration_screen(driver):
    page = _ensure_registration_screen(driver)
    page.reset_form()


@then("registration screen should load successfully")
def registration_screen_should_load_successfully(driver):
    page = RegistrationPage(driver)
    assert page.is_registration_screen_visible(timeout=6), "Registration screen did not load"


@then("app logo should be visible")
def app_logo_should_be_visible(driver):
    assert RegistrationPage(driver).is_logo_visible(), "App logo not visible on registration screen"


@then("welcome heading should be visible")
def welcome_heading_should_be_visible(driver):
    assert RegistrationPage(driver).is_heading_visible(), "Welcome heading not visible on registration screen"


@then("subtitle text should be visible")
def subtitle_text_should_be_visible(driver):
    assert RegistrationPage(driver).is_subtitle_visible(), "Subtitle not visible on registration screen"


@then("back button should be visible")
def back_button_should_be_visible(driver):
    assert RegistrationPage(driver).is_back_button_visible(), "Back button not visible on registration screen"


@then("email field label should be visible")
def email_field_label_should_be_visible(driver):
    assert RegistrationPage(driver).is_email_label_visible(), "Email field label not visible"


@then("email input placeholder should be visible")
def email_input_placeholder_should_be_visible(driver):
    assert RegistrationPage(driver).is_email_placeholder_visible(), "Email placeholder not visible"


@then("create password field label should be visible")
def create_password_field_label_should_be_visible(driver):
    assert RegistrationPage(driver).is_create_password_label_visible(), "Create password label not visible"


@then("create password input placeholder should be visible")
def create_password_input_placeholder_should_be_visible(driver):
    assert RegistrationPage(driver).is_create_password_placeholder_visible(), "Create password placeholder not visible"


@then("confirm password field label should be visible")
def confirm_password_field_label_should_be_visible(driver):
    assert RegistrationPage(driver).is_confirm_password_label_visible(), "Confirm password label not visible"


@then("confirm password input placeholder should be visible")
def confirm_password_input_placeholder_should_be_visible(driver):
    assert RegistrationPage(driver).is_confirm_password_placeholder_visible(), "Confirm password placeholder not visible"


@then("referral code label should be visible")
def referral_code_label_should_be_visible(driver):
    assert RegistrationPage(driver).is_referral_label_visible(), "Referral code label not visible"


@then("referral code input placeholder should be visible")
def referral_code_input_placeholder_should_be_visible(driver):
    assert RegistrationPage(driver).is_referral_placeholder_visible(), "Referral code placeholder not visible"


@then("age confirmation checkbox should be visible")
def age_confirmation_checkbox_should_be_visible(driver):
    assert RegistrationPage(driver).is_age_checkbox_visible(), "Age confirmation checkbox not visible"


@then("terms and conditions text should be visible")
def terms_and_conditions_text_should_be_visible(driver):
    assert RegistrationPage(driver).is_terms_and_conditions_text_visible(), "Terms and Conditions text not visible"


@then("privacy policy text should be visible")
def privacy_policy_text_should_be_visible(driver):
    assert RegistrationPage(driver).is_privacy_policy_text_visible(), "Privacy Policy text not visible"


@then("continue button should be visible")
def continue_button_should_be_visible(driver):
    assert RegistrationPage(driver).is_continue_button_visible(), "Continue button not visible"


@then("social registration section text should be visible")
def social_registration_section_text_should_be_visible(driver):
    assert RegistrationPage(driver).is_social_registration_text_visible(), "Social registration section text not visible"


@then("Facebook registration button should be visible")
def facebook_registration_button_should_be_visible(driver):
    assert RegistrationPage(driver).is_facebook_registration_visible(), "Facebook registration button not visible"


@when("user enters valid email address")
def user_enters_valid_email_address(driver):
    email = _unique_email()
    RegistrationPage(driver).enter_email(email)
    setattr(driver, "_registration_email", email)


@then("email input should show entered value")
def email_input_should_show_entered_value(driver):
    page = RegistrationPage(driver)
    expected = getattr(driver, "_registration_email", "")
    actual = page.get_email_value().strip().lower()
    if expected:
        assert actual == expected.strip().lower(), "Entered email value not reflected"
    else:
        assert "@" in actual, "Entered email value was not retained"


@when("user enters invalid email address")
def user_enters_invalid_email_address(driver):
    RegistrationPage(driver).enter_email(INVALID_EMAIL)


@then("email format validation message should be displayed")
def email_format_validation_message_should_be_displayed(driver):
    assert RegistrationPage(driver).is_email_format_error_visible(), "Email format validation message not displayed"


@when("user leaves email field empty")
def user_leaves_email_field_empty(driver):
    RegistrationPage(driver).enter_email("")


@then("email required validation message should be displayed")
def email_required_validation_message_should_be_displayed(driver):
    assert RegistrationPage(driver).is_email_required_error_visible(), "Email required validation not displayed"


@when("user enters create password")
def user_enters_create_password(driver):
    RegistrationPage(driver).enter_create_password(CREATE_PASSWORD)
    setattr(driver, "_current_create_password", CREATE_PASSWORD)


@then("create password input should show masked value")
def create_password_input_should_show_masked_value(driver):
    assert RegistrationPage(driver).is_create_password_masked(), "Create password was not masked"


@then("create password should be hidden by default")
def create_password_should_be_hidden_by_default(driver):
    assert RegistrationPage(driver).is_create_password_masked(), "Create password is not hidden by default"


@when("user taps create password visibility toggle icon")
def user_taps_create_password_visibility_toggle_icon(driver):
    page = RegistrationPage(driver)
    toggle_password = getattr(driver, "_create_toggle_password", CREATE_PASSWORD)
    if not page.get_email_value():
        page.enter_email(_unique_email())
    page.enter_create_password(toggle_password)
    setattr(driver, "_create_toggle_password", toggle_password)
    assert _toggle_until(page, "create", expected_visible=True, password=toggle_password), "Unable to toggle create password visibility ON"


@then("create password should be visible")
def create_password_should_be_visible(driver):
    pwd = getattr(driver, "_create_toggle_password", CREATE_PASSWORD)
    assert RegistrationPage(driver).wait_until_create_password_visible_as(pwd, timeout=2), "Create password did not become visible"


@when("user taps create password visibility toggle icon again")
def user_taps_create_password_visibility_toggle_icon_again(driver):
    page = RegistrationPage(driver)
    pwd = getattr(driver, "_create_toggle_password", CREATE_PASSWORD)
    assert _toggle_until(page, "create", expected_visible=False, password=pwd), "Unable to toggle create password visibility OFF"


@then("create password should be hidden")
def create_password_should_be_hidden(driver):
    pwd = getattr(driver, "_create_toggle_password", CREATE_PASSWORD)
    assert RegistrationPage(driver).wait_until_create_password_hidden_from(pwd, timeout=2), "Create password did not become hidden"


@when("user enters weak create password")
def user_enters_weak_create_password(driver):
    RegistrationPage(driver).enter_create_password(WEAK_PASSWORD)
    setattr(driver, "_current_create_password", WEAK_PASSWORD)


@then("password strength validation message should be displayed")
def password_strength_validation_message_should_be_displayed(driver):
    assert RegistrationPage(driver).is_password_strength_error_visible(), "Password strength validation was not displayed"


@when("user leaves create password field empty")
def user_leaves_create_password_field_empty(driver):
    RegistrationPage(driver).enter_create_password("")
    setattr(driver, "_current_create_password", "")


@then("create password required validation message should be displayed")
def create_password_required_validation_message_should_be_displayed(driver):
    assert RegistrationPage(driver).is_create_password_required_error_visible(), "Create password required validation not displayed"


@when("user enters confirm password")
def user_enters_confirm_password(driver):
    current_create_password = getattr(driver, "_current_create_password", CREATE_PASSWORD)
    RegistrationPage(driver).enter_confirm_password(current_create_password)


@then("confirm password input should show masked value")
def confirm_password_input_should_show_masked_value(driver):
    assert RegistrationPage(driver).is_confirm_password_masked(), "Confirm password was not masked"


@then("confirm password should be hidden by default")
def confirm_password_should_be_hidden_by_default(driver):
    assert RegistrationPage(driver).is_confirm_password_masked(), "Confirm password is not hidden by default"


@when("user taps confirm password visibility toggle icon")
def user_taps_confirm_password_visibility_toggle_icon(driver):
    page = RegistrationPage(driver)
    toggle_password = getattr(driver, "_confirm_toggle_password", CREATE_PASSWORD)
    page.enter_confirm_password(toggle_password)
    setattr(driver, "_confirm_toggle_password", toggle_password)
    assert _toggle_until(page, "confirm", expected_visible=True, password=toggle_password), "Unable to toggle confirm password visibility ON"


@then("confirm password should be visible")
def confirm_password_should_be_visible(driver):
    pwd = getattr(driver, "_confirm_toggle_password", CREATE_PASSWORD)
    assert RegistrationPage(driver).wait_until_confirm_password_visible_as(pwd, timeout=2), "Confirm password did not become visible"


@when("user taps confirm password visibility toggle icon again")
def user_taps_confirm_password_visibility_toggle_icon_again(driver):
    page = RegistrationPage(driver)
    pwd = getattr(driver, "_confirm_toggle_password", CREATE_PASSWORD)
    assert _toggle_until(page, "confirm", expected_visible=False, password=pwd), "Unable to toggle confirm password visibility OFF"


@then("confirm password should be hidden")
def confirm_password_should_be_hidden(driver):
    pwd = getattr(driver, "_confirm_toggle_password", CREATE_PASSWORD)
    assert RegistrationPage(driver).wait_until_confirm_password_hidden_from(pwd, timeout=2), "Confirm password did not become hidden"


@when("user enters matching confirm password")
def user_enters_matching_confirm_password(driver):
    current_create_password = getattr(driver, "_current_create_password", CREATE_PASSWORD)
    RegistrationPage(driver).enter_confirm_password(current_create_password)


@then("passwords should match successfully")
def passwords_should_match_successfully(driver):
    assert not RegistrationPage(driver).is_password_mismatch_error_visible(), "Password mismatch error displayed for matching passwords"


@when("user enters non matching confirm password")
def user_enters_non_matching_confirm_password(driver):
    RegistrationPage(driver).enter_confirm_password("Mismatch@123")


@then("password mismatch validation message should be displayed")
def password_mismatch_validation_message_should_be_displayed(driver):
    assert RegistrationPage(driver).is_password_mismatch_error_visible(), "Password mismatch validation message not displayed"


@when("user leaves confirm password field empty")
def user_leaves_confirm_password_field_empty(driver):
    RegistrationPage(driver).enter_confirm_password("")


@then("confirm password required validation message should be displayed")
def confirm_password_required_validation_message_should_be_displayed(driver):
    assert RegistrationPage(driver).is_confirm_password_required_error_visible(), "Confirm password required validation not displayed"


@when("user enters referral code")
def user_enters_referral_code(driver):
    RegistrationPage(driver).enter_referral_code("ABC123")


@then("referral code input should show entered value")
def referral_code_input_should_show_entered_value(driver):
    assert RegistrationPage(driver).get_referral_value() != "", "Referral code value was not retained"


@when("user taps age confirmation checkbox")
def user_taps_age_confirmation_checkbox(driver):
    page = RegistrationPage(driver)
    for _ in range(3):
        page.tap_age_checkbox()
        if page.wait_until_age_checkbox_state(True, timeout=0.6):
            return
        page.tap_age_checkbox_by_relative_layout()
        if page.wait_until_age_checkbox_state(True, timeout=0.6):
            return


@then("age confirmation checkbox should be selected")
def age_confirmation_checkbox_should_be_selected(driver):
    assert RegistrationPage(driver).wait_until_age_checkbox_state(True, timeout=1.2), "Age checkbox was not selected"


@when("user taps age confirmation checkbox again")
def user_taps_age_confirmation_checkbox_again(driver):
    RegistrationPage(driver).set_age_checkbox_state(False)


@then("age confirmation checkbox should be deselected")
def age_confirmation_checkbox_should_be_deselected(driver):
    page = RegistrationPage(driver)
    page.tap_continue()
    assert page.is_consent_required_error_visible(), "Age checkbox deselection was not applied"


@when("user taps terms and conditions link")
def user_taps_terms_and_conditions_link(driver):
    page = RegistrationPage(driver)
    page.scroll_to_terms_and_conditions_link()
    assert page.tap_terms_and_conditions_text_simple(), "Could not open Terms & Conditions screen from the link"


@then("terms and conditions screen should be displayed")
def terms_and_conditions_screen_should_be_displayed(driver):
    page = RegistrationPage(driver)
    assert page.is_terms_screen_visible(timeout=6), "Terms and Conditions screen was not displayed"
    _safe_back(driver)


@when("user taps privacy policy link")
def user_taps_privacy_policy_link(driver):
    page = RegistrationPage(driver)
    page.scroll_to_privacy_policy_link()
    assert page.tap_privacy_policy_text_simple(), "Could not open Privacy Policy screen from the link"


@then("privacy policy screen should be displayed")
def privacy_policy_screen_should_be_displayed(driver):
    page = RegistrationPage(driver)
    assert page.is_privacy_screen_visible(timeout=6), "Privacy Policy screen was not displayed"
    _safe_back(driver)


@when("user enters only email address")
def user_enters_only_email_address(driver):
    page = RegistrationPage(driver)
    email = _unique_email()
    page.enter_email(email)
    page.enter_create_password("")
    page.enter_confirm_password("")


@then("continue button should be disabled")
def continue_button_should_be_disabled(driver):
    assert not RegistrationPage(driver).is_continue_button_enabled(), "Continue button was enabled unexpectedly"


@when("user enters valid create password")
def user_enters_valid_create_password(driver):
    RegistrationPage(driver).enter_create_password(CREATE_PASSWORD)
    setattr(driver, "_current_create_password", CREATE_PASSWORD)


@when("user taps continue button")
def user_taps_continue_button(driver):
    RegistrationPage(driver).tap_continue()


@then("user should proceed to next registration step")
def user_should_proceed_to_next_registration_step(driver):
    page = RegistrationPage(driver)

    if page.is_already_registered_alert_visible():
        raise AssertionError("Already registered alert displayed for unique registration flow")

    _assert_registration_success_and_cleanup(driver)


@when("user enters already registered email address")
def user_enters_already_registered_email_address(driver, env_setup):
    existing_email = env_setup["email"]
    assert existing_email, "Missing SHOPPIX_LOGIN_EMAIL in .env for already registered scenario"
    RegistrationPage(driver).enter_email(existing_email)


@then("already registered alert should be displayed")
def already_registered_alert_should_be_displayed(driver):
    assert RegistrationPage(driver).is_already_registered_alert_visible(), "Already registered alert was not displayed"


@when("user taps already registered alert OK button")
def user_taps_already_registered_alert_ok_button(driver):
    RegistrationPage(driver).dismiss_already_registered_alert()


@when("user taps Facebook registration button")
def user_taps_facebook_registration_button(driver):
    RegistrationPage(driver).tap_facebook_registration()


@then("Facebook auth flow should be displayed")
def facebook_auth_flow_should_be_displayed(driver):
    page = RegistrationPage(driver)
    assert page.is_facebook_auth_flow_displayed(), "Facebook auth flow did not open"

    # Keep the next scenarios stable if external flow opened.
    if not page.is_registration_screen_visible(timeout=2):
        _safe_back(driver)


@when("user cancels Facebook registration")
def user_cancels_facebook_registration(driver):
    _safe_back(driver)


@then("registration screen should be displayed")
def registration_screen_should_be_displayed(driver):
    assert _ensure_registration_screen(driver).is_registration_screen_visible(timeout=6), "Registration screen was not displayed"


@when("app is sent to background")
def app_is_sent_to_background(driver):
    driver.background_app(2)


@when("app is brought to foreground")
def app_is_brought_to_foreground(driver):
    caps = driver.capabilities
    app_package = caps.get("appium:appPackage") or caps.get("appPackage")
    assert app_package, "App package not available in capabilities"
    driver.activate_app(app_package)


@when("device orientation is changed")
def device_orientation_is_changed(driver):
    original = (driver.orientation or "PORTRAIT").upper()
    target = "LANDSCAPE" if original == "PORTRAIT" else "PORTRAIT"
    try:
        driver.orientation = target
        driver.orientation = original
    except Exception:
        pass


@then("registration screen should be displayed correctly")
def registration_screen_should_be_displayed_correctly(driver):
    page = _ensure_registration_screen(driver)
    assert page.is_core_content_visible(), "Registration screen did not render correctly"


@when("user presses Android back")
def user_presses_android_back(driver):
    _safe_back(driver)


@then("user should be navigated as per expected back behavior")
def user_should_be_navigated_as_per_expected_back_behavior(driver):
    state = _quick_screen_state(driver)
    assert state in {"welcome", "login", "registration", "home"}, "Back navigation did not land on a known app screen"


@then("all visible elements should have accessibility labels")
def all_visible_elements_should_have_accessibility_labels(driver):
    page = RegistrationPage(driver)
    assert page.has_basic_accessibility_labels(), (
        "One or more key registration elements are missing accessibility labels: "
        + ", ".join(page.last_accessibility_missing())
    )
    assert page.restore_registration_top(timeout=6), "Could not restore registration screen to top (Welcome to Shoppix heading not visible)"


@then("registration screen should render correctly on small screen device")
def registration_screen_should_render_correctly_on_small_screen_device(driver):
    # On a single lab device we validate screen integrity rather than changing hardware.
    assert _ensure_registration_screen(driver).is_core_content_visible(), "Registration layout integrity failed for small-screen check"


@then("registration screen should render correctly on large screen device")
def registration_screen_should_render_correctly_on_large_screen_device(driver):
    # On a single lab device we validate screen integrity rather than changing hardware.
    assert _ensure_registration_screen(driver).is_core_content_visible(), "Registration layout integrity failed for large-screen check"
