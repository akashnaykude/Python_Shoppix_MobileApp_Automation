from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class LoginPage:
    WELCOME_TITLE = (AppiumBy.XPATH, "//android.widget.TextView[@text='Welcome Back!']")
    EMAIL_INPUT = (AppiumBy.XPATH, "//android.widget.EditText[1]")
    PASSWORD_INPUT = (AppiumBy.XPATH, "//android.widget.EditText[2]")
    LOGIN_TEXT = (AppiumBy.XPATH, "//android.widget.TextView[@text='Login']")
    LOGIN_CONTAINER = (
        AppiumBy.XPATH,
        "//android.widget.TextView[@text='Login']/ancestor::android.view.View[@clickable='true'][1]",
    )

    LETS_GET_STARTED = (
        AppiumBy.XPATH,
        "//android.widget.TextView[@text=\"Let's get started\" or @text='Lets get started' or @text='Let’s get started']",
    )
    WELCOME_LOGIN_CTA = (
        AppiumBy.XPATH,
        "//android.widget.TextView[@text='Login as existing User']/ancestor::android.view.View[@clickable='true'][1]",
    )

    ALERT_TITLE = (AppiumBy.XPATH, "//android.widget.TextView[@text='Sorry']")
    ALERT_MESSAGE = (AppiumBy.XPATH, "//android.widget.TextView")
    ALERT_OK = (AppiumBy.XPATH, "//android.widget.TextView[@text='OK']")

    EMAIL_PLACEHOLDER = (AppiumBy.XPATH, "//android.widget.TextView[@text='Enter your email']")
    PASSWORD_PLACEHOLDER = (AppiumBy.XPATH, "//android.widget.TextView[@text='Enter your password']")
    EMAIL_LABEL = (AppiumBy.XPATH, "//android.widget.TextView[@text='Email']")
    PASSWORD_LABEL = (AppiumBy.XPATH, "//android.widget.TextView[@text='Password']")

    def __init__(self, driver):
        self.driver = driver

    def _find(self, locator, timeout: int = 20):
        return WebDriverWait(self.driver, timeout).until(ec.presence_of_element_located(locator))

    def _find_clickable(self, locator, timeout: int = 20):
        return WebDriverWait(self.driver, timeout).until(ec.element_to_be_clickable(locator))

    def _is_visible(self, locator, timeout: int = 10) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(ec.visibility_of_element_located(locator))
            return True
        except Exception:
            return False

    def navigate_to_login_if_needed(self):
        if self._is_visible(self.WELCOME_TITLE, timeout=6):
            return

        if self._is_visible(self.WELCOME_LOGIN_CTA, timeout=6):
            self._find_clickable(self.WELCOME_LOGIN_CTA, timeout=8).click()
            self._find(self.WELCOME_TITLE, timeout=15)
            return

        if self._is_visible(self.LETS_GET_STARTED, timeout=6):
            self._find_clickable(self.LETS_GET_STARTED, timeout=5).click()
            self._find(self.WELCOME_TITLE, timeout=15)

    def is_login_screen_visible(self, timeout: int = 10) -> bool:
        return self._is_visible(self.WELCOME_TITLE, timeout=timeout)

    def are_placeholders_visible(self) -> bool:
        return self._is_visible(self.EMAIL_PLACEHOLDER, timeout=6) and self._is_visible(self.PASSWORD_PLACEHOLDER, timeout=6)

    def are_field_labels_visible(self) -> bool:
        return self._is_visible(self.EMAIL_LABEL, timeout=6) and self._is_visible(self.PASSWORD_LABEL, timeout=6)

    def is_email_field_ready(self) -> bool:
        if self._is_visible(self.EMAIL_PLACEHOLDER, timeout=2):
            return True
        try:
            email_text = (self._find(self.EMAIL_INPUT, timeout=5).get_attribute("text") or "").strip()
            return bool(email_text)
        except Exception:
            return False

    def is_password_placeholder_visible(self) -> bool:
        return self._is_visible(self.PASSWORD_PLACEHOLDER, timeout=6)

    def enter_email(self, email: str):
        elem = self._find(self.EMAIL_INPUT, timeout=15)
        elem.clear()
        elem.send_keys(email)

    def enter_password(self, password: str):
        elem = self._find(self.PASSWORD_INPUT, timeout=15)
        elem.clear()
        elem.send_keys(password)

    def reset_form(self):
        try:
            self._find(self.EMAIL_INPUT, timeout=5).clear()
        except Exception:
            pass
        try:
            self._find(self.PASSWORD_INPUT, timeout=5).clear()
        except Exception:
            pass
        try:
            self.driver.hide_keyboard()
        except Exception:
            pass

    def tap_login(self):
        # Dismiss soft keyboard so login CTA is not hidden by IME.
        try:
            self.driver.hide_keyboard()
        except Exception:
            pass

        if self._is_visible(self.LOGIN_CONTAINER, timeout=5):
            self._find_clickable(self.LOGIN_CONTAINER, timeout=8).click()
            return

        self._find_clickable(self.LOGIN_TEXT, timeout=5).click()

    def is_login_button_enabled(self) -> bool:
        try:
            elem = self._find(self.LOGIN_CONTAINER, timeout=6)
            return str(elem.get_attribute("enabled")).lower() == "true"
        except Exception:
            return False

    def login_with_credentials(self, email: str, password: str):
        self.enter_email(email)
        self.enter_password(password)
        self.tap_login()

    def get_invalid_alert(self, allowed_messages: list[str], timeout: int = 15):
        self._find(self.ALERT_TITLE, timeout=timeout)
        for message in allowed_messages:
            locator = (AppiumBy.XPATH, f"//android.widget.TextView[@text=\"{message}\"]")
            if self._is_visible(locator, timeout=3):
                return "Sorry", message
        return "Sorry", ""

    def dismiss_invalid_alert(self):
        self._find(self.ALERT_OK, timeout=10).click()

    def is_invalid_alert_visible(self, timeout: int = 5) -> bool:
        return self._is_visible(self.ALERT_TITLE, timeout=timeout)
