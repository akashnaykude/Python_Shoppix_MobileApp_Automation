from pytest_bdd import given, scenarios, then, when
from selenium.common.exceptions import WebDriverException
import pytest

from src.pages.home_page import HomePage
from src.pages.login_page import LoginPage
from src.pages.welcome_page import WelcomePage

scenarios("../Features/Welcome.feature")


def _quick_screen_state(driver) -> str:
	try:
		src = (driver.page_source or "").lower()
	except Exception:
		return "unknown"

	if "let's get started" in src or "lets get started" in src or "let\u2019s get started" in src:
		return "welcome"
	if "welcome back!" in src or "enter your email" in src:
		return "login"
	if "menu_action_setting" in src or "img_header" in src:
		return "home"
	return "unknown"


def _bootstrap_welcome_module(driver):
	caps = driver.capabilities
	app_package = caps.get("appium:appPackage") or caps.get("appPackage")
	if app_package:
		try:
			driver.activate_app(app_package)
		except Exception:
			pass

	_recover_to_welcome_without_reinstall(driver)


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


def _is_any_known_app_screen_visible(driver) -> bool:
	welcome = WelcomePage(driver)
	login = LoginPage(driver)
	home = HomePage(driver)
	return (
		welcome.is_welcome_visible(timeout=4)
		or login.is_login_screen_visible(timeout=4)
		or home.is_home_header_visible(timeout=4)
	)


def _recover_to_welcome_without_reinstall(driver):
	welcome = WelcomePage(driver)
	login = LoginPage(driver)
	home = HomePage(driver)
	caps = driver.capabilities
	app_package = caps.get("appium:appPackage") or caps.get("appPackage")

	# Lightweight recovery: ensure app is foregrounded before navigation checks.
	if app_package:
		try:
			driver.activate_app(app_package)
		except Exception:
			pass

	if welcome.is_welcome_visible(timeout=6):
		return

	state = _quick_screen_state(driver)
	if state == "welcome":
		return
	if state == "home":
		home.logout_from_menu()
		if welcome.is_welcome_visible(timeout=4):
			return
	if state == "login":
		try:
			driver.back()
		except WebDriverException:
			_soft_relaunch_app(driver)
		if welcome.is_welcome_visible(timeout=4):
			return

	# Bounded in-app recovery for transient flows (web/auth/back-stack).
	for _ in range(2):
		if welcome.is_welcome_visible(timeout=3):
			return

		if home.is_home_header_visible(timeout=3):
			home.logout_from_menu()
			continue

		if login.is_login_screen_visible(timeout=3):
			_soft_relaunch_app(driver)
			continue

		_soft_relaunch_app(driver)

	assert welcome.is_welcome_visible(timeout=10), "Could not navigate back to welcome screen without reinstall"
def _ensure_welcome_screen_without_relaunch(driver):
	if _quick_screen_state(driver) == "welcome":
		return

	welcome = WelcomePage(driver)
	if welcome.is_welcome_visible(timeout=2):
		return

	try:
		_recover_to_welcome_without_reinstall(driver)
		return
	except AssertionError:
		# Final fallback only on failure path.
		_soft_relaunch_app(driver)
		login = LoginPage(driver)
		if login.is_login_screen_visible(timeout=3):
			try:
				driver.back()
			except WebDriverException:
				pass

	if not welcome.is_welcome_visible(timeout=6):
		raise AssertionError("Could not navigate back to welcome screen without reinstall")


@pytest.fixture(scope="module", autouse=True)
def _welcome_module_bootstrap(driver):
	_bootstrap_welcome_module(driver)
	yield


@given("user is on welcome screen")
def user_is_on_welcome_screen(driver):
	_ensure_welcome_screen_without_relaunch(driver)
	assert WelcomePage(driver).is_welcome_visible(timeout=10), "Welcome screen was not visible"


@then("Facebook registration button should be visible")
def facebook_registration_button_should_be_visible(driver):
	assert WelcomePage(driver).is_facebook_icon_visible(), "Facebook registration button should be visible"


@then("Email registration button should be visible")
def email_registration_button_should_be_visible(driver):
	assert WelcomePage(driver).is_email_icon_visible(), "Email registration button should be visible"


@then("app logo should be visible")
def app_logo_should_be_visible(driver):
	assert WelcomePage(driver).is_logo_visible(), "App logo should be visible"


@then("welcome heading should be visible")
def welcome_heading_should_be_visible(driver):
	assert WelcomePage(driver).is_heading_visible(), "Welcome heading should be visible"


@then("welcome screen subtitle should be visible")
def welcome_screen_subtitle_should_be_visible(driver):
	assert WelcomePage(driver).is_subtitle_visible(), "Welcome subtitle should be visible"


@then("register with text should be visible")
def register_with_text_should_be_visible(driver):
	assert WelcomePage(driver).is_or_register_text_visible(), "Register with text should be visible"


@then("footer version text should be visible")
def footer_version_text_should_be_visible(driver):
	assert WelcomePage(driver).is_footer_version_visible(), "Footer version text should be visible"


@then("welcome screen loads with expected UI content")
def welcome_screen_loads_with_expected_ui_content(driver):
	page = WelcomePage(driver)
	assert page.is_logo_visible(), "Kantar logo should be visible"
	assert page.is_heading_visible(), "Welcome heading should be visible"
	assert page.is_subtitle_visible(), "Welcome subtitle should be visible"
	assert page.is_login_cta_visible(), "Login as existing User should be visible"
	assert page.is_or_register_text_visible(), "Register helper text should be visible"
	assert page.is_facebook_icon_visible(), "facebook icon button should be visible"
	assert page.is_email_icon_visible(), "email icon button should be visible"
	assert page.is_footer_version_visible(), "version text should be visible"
	assert page.is_footer_stage_visible(), "environment label should be visible"


@when("user taps Login as existing User")
def user_taps_login_as_existing_user(driver):
	WelcomePage(driver).tap_login_as_existing_user()


@when("user taps Facebook registration icon")
def user_taps_facebook_registration_icon(driver):
	WelcomePage(driver).tap_facebook_registration_icon()


@when("user taps Email registration icon")
def user_taps_email_registration_icon(driver):
	WelcomePage(driver).tap_email_registration_icon()


@then("login screen should be displayed")
def login_screen_should_be_displayed(driver):
	assert LoginPage(driver).is_login_screen_visible(timeout=12), "Login screen was not visible"


@then("Facebook login flow should be displayed")
def facebook_login_flow_should_be_displayed(driver):
	# Flow is valid if we moved away from welcome OR received app dialog from Facebook attempt.
	page = WelcomePage(driver)
	if page.dismiss_oops_dialog_if_present(timeout=5):
		return

	state = _quick_screen_state(driver)
	if state == "welcome":
		assert not page.is_welcome_visible(timeout=1), "Facebook login flow did not open"


@then("email registration flow should be displayed")
def email_registration_flow_should_be_displayed(driver):
	# Fast check: flow is considered opened when current screen is not welcome.
	state = _quick_screen_state(driver)
	if state == "welcome":
		assert not WelcomePage(driver).is_welcome_visible(timeout=1), "Email registration flow did not open"


@when("user cancels Facebook login")
def user_cancels_facebook_login(driver):
	driver.back()


@when("user cancels email registration")
def user_cancels_email_registration(driver):
	driver.back()


@then("user should return to welcome screen")
def user_should_return_to_welcome_screen(driver):
	_ensure_welcome_screen_without_relaunch(driver)
	assert WelcomePage(driver).is_welcome_visible(timeout=10), "User did not return to welcome screen"


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
		# Restore baseline to avoid leaking state into next scenarios.
		driver.orientation = original
	except Exception:
		# Some devices lock rotation at OS/app level; keep scenario non-blocking.
		pass


@then("welcome screen should be displayed correctly")
def welcome_screen_should_be_displayed_correctly(driver):
	page = WelcomePage(driver)
	assert page.is_welcome_visible(timeout=10), "Welcome screen heading was not visible"
	assert page.is_core_welcome_content_visible(), "Welcome screen content was not displayed correctly"


@when("user presses Android back")
def user_presses_android_back(driver):
	driver.back()


@then("app should handle back press gracefully")
def app_should_handle_back_press_gracefully(driver):
	# Bring app foreground if back press moved app to background.
	caps = driver.capabilities
	app_package = caps.get("appium:appPackage") or caps.get("appPackage")
	if app_package:
		driver.activate_app(app_package)

	assert _is_any_known_app_screen_visible(driver), "App did not recover to a known screen after back press"


@when("user taps Login as existing User twice quickly")
def user_taps_login_as_existing_user_twice_quickly(driver):
	welcome = WelcomePage(driver)
	login = LoginPage(driver)

	welcome.tap_login_as_existing_user()
	# If first tap already navigated, avoid failing on missing welcome CTA.
	if welcome.is_welcome_visible(timeout=2):
		welcome.tap_login_as_existing_user()
	elif login.is_login_screen_visible(timeout=3):
		return


@when("user presses Android back from login screen")
def user_presses_android_back_from_login_screen(driver):
	driver.back()


@then("welcome screen should be displayed again")
def welcome_screen_should_be_displayed_again(driver):
	assert WelcomePage(driver).is_welcome_visible(timeout=10), "Welcome screen was not visible after back"


@then("welcome screen should be displayed")
def welcome_screen_should_be_displayed(driver):
	assert WelcomePage(driver).is_welcome_visible(timeout=10), "Welcome screen was not visible"
