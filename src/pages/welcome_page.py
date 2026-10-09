from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class WelcomePage:
	HEADING = (
		AppiumBy.XPATH,
		"//android.widget.TextView[@text=\"Let's get started\" or @text=\"Lets get started\" or @text=\"Let’s get started\"]",
	)
	SUBTITLE = (
		AppiumBy.XPATH,
		"//android.widget.TextView[contains(@text, 'Submit receipts') and contains(@text, 'earn rewards')]",
	)
	LOGIN_EXISTING_USER_TEXT = (AppiumBy.XPATH, "//android.widget.TextView[@text='Login as existing User']")
	LOGIN_EXISTING_USER_CTA = (
		AppiumBy.XPATH,
		"//android.widget.TextView[@text='Login as existing User']/ancestor::android.view.View[@clickable='true'][1]",
	)
	OR_REGISTER_TEXT = (AppiumBy.XPATH, "//android.widget.TextView[@text='or register with:']")
	FACEBOOK_ICON = (AppiumBy.XPATH, "//android.widget.ImageView[@content-desc='Register with Facebook']")
	EMAIL_ICON = (AppiumBy.XPATH, "//android.widget.ImageView[@content-desc='Register with Email']")
	FOOTER_VERSION = (AppiumBy.XPATH, "//android.widget.TextView[contains(@text, 'Shoppix:')]")
	FOOTER_STAGE = (AppiumBy.XPATH, "//android.widget.TextView[contains(@text, 'Stage')]")
	KANTAR_LOGO = (AppiumBy.XPATH, "//android.widget.ImageView[@content-desc='Kantar Logo']")
	OOPS_TITLE = (AppiumBy.XPATH, "//android.widget.TextView[@text='Oops']")
	OOPS_OK_CTA = (
		AppiumBy.XPATH,
		"//android.widget.TextView[@text='OK']/ancestor::android.view.View[@clickable='true'][1]",
	)
	OOPS_OK_BUTTON = (AppiumBy.XPATH, "//android.widget.Button[ancestor::*[@pane-title='Dialogue']]")

	def __init__(self, driver):
		self.driver = driver

	def _is_visible(self, locator, timeout: int = 8) -> bool:
		try:
			WebDriverWait(self.driver, timeout).until(ec.visibility_of_element_located(locator))
			return True
		except Exception:
			return False

	def _find_clickable(self, locator, timeout: int = 12):
		return WebDriverWait(self.driver, timeout).until(ec.element_to_be_clickable(locator))

	def is_welcome_visible(self, timeout: int = 10) -> bool:
		return self._is_visible(self.HEADING, timeout=timeout)

	def tap_login_as_existing_user(self):
		self._find_clickable(self.LOGIN_EXISTING_USER_CTA, timeout=12).click()

	def tap_facebook_registration_icon(self):
		self._find_clickable(self.FACEBOOK_ICON, timeout=12).click()

	def tap_email_registration_icon(self):
		self._find_clickable(self.EMAIL_ICON, timeout=12).click()

	def is_logo_visible(self) -> bool:
		return self._is_visible(self.KANTAR_LOGO, timeout=8)

	def is_heading_visible(self) -> bool:
		return self._is_visible(self.HEADING, timeout=8)

	def is_subtitle_visible(self) -> bool:
		return self._is_visible(self.SUBTITLE, timeout=8)

	def is_login_cta_visible(self) -> bool:
		return self._is_visible(self.LOGIN_EXISTING_USER_TEXT, timeout=8)

	def is_or_register_text_visible(self) -> bool:
		return self._is_visible(self.OR_REGISTER_TEXT, timeout=8)

	def is_facebook_icon_visible(self) -> bool:
		return self._is_visible(self.FACEBOOK_ICON, timeout=8)

	def is_email_icon_visible(self) -> bool:
		return self._is_visible(self.EMAIL_ICON, timeout=8)

	def is_footer_version_visible(self) -> bool:
		return self._is_visible(self.FOOTER_VERSION, timeout=8)

	def is_footer_stage_visible(self) -> bool:
		return self._is_visible(self.FOOTER_STAGE, timeout=8)

	def is_core_welcome_content_visible(self) -> bool:
		return (
			self.is_logo_visible()
			and self.is_heading_visible()
			and self.is_subtitle_visible()
			and self.is_login_cta_visible()
			and self.is_or_register_text_visible()
		)

	def is_oops_dialog_visible(self, timeout: int = 2) -> bool:
		return self._is_visible(self.OOPS_TITLE, timeout=timeout)

	def dismiss_oops_dialog_if_present(self, timeout: int = 2) -> bool:
		if not self.is_oops_dialog_visible(timeout=timeout):
			return False

		try:
			self._find_clickable(self.OOPS_OK_CTA, timeout=3).click()
			return True
		except Exception:
			pass

		try:
			self._find_clickable(self.OOPS_OK_BUTTON, timeout=3).click()
			return True
		except Exception:
			return False
