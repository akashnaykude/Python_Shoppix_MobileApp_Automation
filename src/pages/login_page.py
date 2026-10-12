from appium.webdriver.common.appiumby import AppiumBy
import time
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class LoginPage:
    APP_LOGO = (AppiumBy.XPATH, "//android.widget.ImageView[@content-desc='Kantar Logo']")
    WELCOME_TITLE = (AppiumBy.XPATH, "//android.widget.TextView[@text='Welcome Back!']")
    SUBTITLE = (
        AppiumBy.XPATH,
        "//android.widget.TextView[contains(@text, 'Submit receipts') and contains(@text, 'earn rewards')]",
    )
    EMAIL_INPUT = (AppiumBy.XPATH, "//android.widget.EditText[1]")
    PASSWORD_INPUT = (AppiumBy.XPATH, "//android.widget.EditText[2]")
    PASSWORD_TOGGLE = (AppiumBy.XPATH, "//android.widget.EditText[2]//android.widget.Button")
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
    FORGOT_PASSWORD = (AppiumBy.XPATH, "//android.widget.TextView[contains(@text, 'Forgot Password')]")
    FORGOT_PASSWORD_HEADING = (
        AppiumBy.XPATH,
        "//android.widget.TextView[contains(@text, 'Forgot your password')]",
    )
    FORGOT_PASSWORD_DESCRIPTION = (
        AppiumBy.XPATH,
        "//android.widget.TextView[contains(@text, 'send you a link to reset your password')]",
    )
    BACK_BUTTON = (AppiumBy.XPATH, "//android.widget.ImageView[@content-desc='Back']")
    SOCIAL_LOGIN_TEXT = (AppiumBy.XPATH, "//android.widget.TextView[contains(@text, 'or login with')]")
    FACEBOOK_LOGIN = (
        AppiumBy.XPATH,
        "//android.widget.ImageView[@content-desc='Connect with Facebook' or @content-desc='Register with Facebook']",
    )
    SIGN_UP_LINK = (AppiumBy.XPATH, "//android.widget.TextView[contains(@text, 'Sign up')]")
    SIGN_UP_CTA = (
        AppiumBy.XPATH,
        "//android.widget.TextView[contains(@text, 'Sign up')]/ancestor::android.view.View[@clickable='true'][1]",
    )
    EMAIL_REQUIRED_ERROR = (AppiumBy.XPATH, "//android.widget.TextView[contains(@text, 'Please enter an email')]" )
    PASSWORD_REQUIRED_ERROR = (AppiumBy.XPATH, "//android.widget.TextView[contains(@text, 'Please enter a password')]" )
    INVALID_EMAIL_ERROR = (AppiumBy.XPATH, "//android.widget.TextView[contains(@text, 'valid email') or contains(@text, 'Invalid')]" )
    OOPS_TITLE = (AppiumBy.XPATH, "//android.widget.TextView[@text='Oops']")
    CONNECTION_ERROR_TITLE = (AppiumBy.XPATH, "//android.widget.TextView[@text='Connection Error']")
    OOPS_OK = (AppiumBy.XPATH, "//android.widget.TextView[@text='OK']")

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
        # Clear any blocking dialog first so taps are not swallowed by a modal.
        self.dismiss_oops_if_present()

        # Route by one source snapshot to avoid serial 6s+6s+6s waits.
        try:
            src = (self.driver.page_source or "").lower()
        except Exception:
            src = ""

        if "welcome back!" in src or "enter your email" in src:
            return

        if "login as existing user" in src or "let's get started" in src or "lets get started" in src:
            try:
                self._find_clickable(self.WELCOME_LOGIN_CTA, timeout=5).click()
                self._find(self.WELCOME_TITLE, timeout=10)
                return
            except Exception:
                pass

        if self._is_visible(self.WELCOME_TITLE, timeout=2):
            return

        if self._is_visible(self.WELCOME_LOGIN_CTA, timeout=3):
            self._find_clickable(self.WELCOME_LOGIN_CTA, timeout=4).click()
            self._find(self.WELCOME_TITLE, timeout=10)

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

    def tap_login(self):
        # Dismiss soft keyboard so login CTA is not hidden by IME.
        try:
            if hasattr(self.driver, "is_keyboard_shown") and self.driver.is_keyboard_shown():
                self.driver.hide_keyboard()
        except Exception:
            pass

        # Fast path: if login CTA exists but is disabled, return immediately.
        try:
            elem = self._find(self.LOGIN_CONTAINER, timeout=2)
            if str(elem.get_attribute("enabled")).lower() != "true":
                return False
            try:
                elem.click()
                return True
            except Exception:
                self._find_clickable(self.LOGIN_CONTAINER, timeout=2).click()
                return True
        except Exception:
            pass

        try:
            self._find_clickable(self.LOGIN_TEXT, timeout=2).click()
            return True
        except Exception:
            pass

        return False

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

    def is_logo_visible(self, timeout: int = 6) -> bool:
        return self._is_visible(self.APP_LOGO, timeout=timeout)

    def is_heading_visible(self, timeout: int = 6) -> bool:
        return self._is_visible(self.WELCOME_TITLE, timeout=timeout)

    def is_subtitle_visible(self, timeout: int = 6) -> bool:
        return self._is_visible(self.SUBTITLE, timeout=timeout)

    def is_email_label_visible(self, timeout: int = 6) -> bool:
        return self._is_visible(self.EMAIL_LABEL, timeout=timeout)

    def is_password_label_visible(self, timeout: int = 6) -> bool:
        return self._is_visible(self.PASSWORD_LABEL, timeout=timeout)

    def is_email_placeholder_visible(self, timeout: int = 6) -> bool:
        return self._is_visible(self.EMAIL_PLACEHOLDER, timeout=timeout)

    def is_password_toggle_visible(self, timeout: int = 6) -> bool:
        return self._is_visible(self.PASSWORD_TOGGLE, timeout=timeout)

    def is_forgot_password_visible(self, timeout: int = 6) -> bool:
        return self._is_visible(self.FORGOT_PASSWORD, timeout=timeout)

    def is_login_button_visible(self, timeout: int = 6) -> bool:
        return self._is_visible(self.LOGIN_TEXT, timeout=timeout)

    def is_social_login_text_visible(self, timeout: int = 6) -> bool:
        return self._is_visible(self.SOCIAL_LOGIN_TEXT, timeout=timeout)

    def is_facebook_login_button_visible(self, timeout: int = 6) -> bool:
        return self._is_visible(self.FACEBOOK_LOGIN, timeout=timeout)

    def is_sign_up_link_visible(self, timeout: int = 6) -> bool:
        return self._is_visible(self.SIGN_UP_LINK, timeout=timeout)

    def get_email_value(self) -> str:
        try:
            return (self._find(self.EMAIL_INPUT, timeout=5).get_attribute("text") or "").strip()
        except Exception:
            return ""

    def is_password_masked(self) -> bool:
        try:
            elem = self._find(self.PASSWORD_INPUT, timeout=5)
            attr_password = str(elem.get_attribute("password")).lower() == "true"
            text_value = elem.get_attribute("text") or ""
            return attr_password or ("•" in text_value)
        except Exception:
            return False

    def tap_password_toggle(self):
        try:
            if hasattr(self.driver, "is_keyboard_shown") and self.driver.is_keyboard_shown():
                self.driver.hide_keyboard()
        except Exception:
            pass

        try:
            self._find_clickable(self.PASSWORD_TOGGLE, timeout=4).click()
            return
        except Exception:
            pass

        elem = self._find(self.PASSWORD_TOGGLE, timeout=4)
        try:
            self.driver.execute_script("mobile: clickGesture", {"elementId": elem.id})
        except Exception:
            elem.click()

    def is_password_visible_now(self) -> bool:
        try:
            elem = self._find(self.PASSWORD_INPUT, timeout=5)
            return str(elem.get_attribute("password")).lower() == "false"
        except Exception:
            return False

    def get_password_value(self) -> str:
        try:
            return (self._find(self.PASSWORD_INPUT, timeout=4).get_attribute("text") or "").strip()
        except Exception:
            return ""

    def is_password_visible_as(self, expected_password: str) -> bool:
        try:
            elem = self._find(self.PASSWORD_INPUT, timeout=4)
            is_visible_attr = str(elem.get_attribute("password")).lower() == "false"
            value = (elem.get_attribute("text") or "").strip()
            return is_visible_attr and value == expected_password
        except Exception:
            return False

    def is_password_hidden_from(self, plain_password: str) -> bool:
        try:
            elem = self._find(self.PASSWORD_INPUT, timeout=4)
            is_masked_attr = str(elem.get_attribute("password")).lower() == "true"
            value = (elem.get_attribute("text") or "").strip()
            return is_masked_attr or value != plain_password
        except Exception:
            return False

    def wait_until_password_visible_as(self, expected_password: str, timeout: float = 2.5) -> bool:
        end = time.time() + timeout
        while time.time() < end:
            if self.is_password_visible_as(expected_password):
                return True
            time.sleep(0.2)
        return False

    def wait_until_password_hidden_from(self, plain_password: str, timeout: float = 2.5) -> bool:
        end = time.time() + timeout
        while time.time() < end:
            if self.is_password_hidden_from(plain_password):
                return True
            time.sleep(0.2)
        return False

    def tap_forgot_password(self):
        self._find_clickable(self.FORGOT_PASSWORD, timeout=8).click()

    def tap_facebook_login(self):
        self._find_clickable(self.FACEBOOK_LOGIN, timeout=8).click()

    def tap_sign_up(self):
        try:
            if hasattr(self.driver, "is_keyboard_shown") and self.driver.is_keyboard_shown():
                self.driver.hide_keyboard()
        except Exception:
            pass

        # Fast path: direct text element click is usually the quickest.
        try:
            self._find(self.SIGN_UP_LINK, timeout=1).click()
            return
        except Exception:
            pass

        try:
            self._find_clickable(self.SIGN_UP_CTA, timeout=1).click()
            return
        except Exception:
            pass

        try:
            self._find_clickable(self.SIGN_UP_LINK, timeout=1).click()
            return
        except Exception:
            pass

        # Fallback for smaller viewports: scroll until "Sign up" is visible.
        try:
            self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView(new UiSelector().textContains("Sign up"))',
            )
        except Exception:
            pass

        try:
            self._find_clickable(self.SIGN_UP_CTA, timeout=2).click()
            return
        except Exception:
            self._find_clickable(self.SIGN_UP_LINK, timeout=2).click()

    def is_forgot_password_screen_visible(self) -> bool:
        # Wait for actual forgot-password page content instead of relying only on raw page source.
        heading_visible = self._is_visible(self.FORGOT_PASSWORD_HEADING, timeout=8)
        if not heading_visible:
            return False

        description_visible = self._is_visible(self.FORGOT_PASSWORD_DESCRIPTION, timeout=3)
        back_visible = self._is_visible(self.BACK_BUTTON, timeout=3)
        return description_visible or back_visible

    def is_sign_up_screen_visible(self) -> bool:
        # Allow a short transition window after tapping sign-up.
        if self.is_login_screen_visible(timeout=1):
            return False

        src = (self.driver.page_source or "").lower()
        return "sign up" in src or "register" in src or "let's get started" in src or "lets get started" in src

    def is_email_format_error_visible(self) -> bool:
        if self._is_visible(self.INVALID_EMAIL_ERROR, timeout=3):
            return True
        src = (self.driver.page_source or "").lower()
        return "invalid" in src and "email" in src

    def is_email_required_error_visible(self) -> bool:
        if self._is_visible(self.EMAIL_REQUIRED_ERROR, timeout=3):
            return True
        src = (self.driver.page_source or "").lower()
        if "please enter an email" in src or "please enter email" in src:
            return True

        # Some builds flag the email field invalid without rendering helper text.
        if 'content-invalid="true"' in src and "enter your email" in src:
            return not bool(self.get_email_value())

        return False

    def is_password_required_error_visible(self) -> bool:
        if self._is_visible(self.PASSWORD_REQUIRED_ERROR, timeout=3):
            return True
        src = (self.driver.page_source or "").lower()
        if "please enter a password" in src or "please enter password" in src:
            return True

        # Some builds mark the field invalid without helper text.
        if 'content-invalid="true"' in src and "enter your password" in src:
            try:
                val = (self._find(self.PASSWORD_INPUT, timeout=2).get_attribute("text") or "").strip()
                return val == ""
            except Exception:
                return True

        return False

    def dismiss_oops_if_present(self) -> bool:
        # Fast source check so the common no-dialog case stays cheap; also covers
        # the 'Connection Error' dialog shown by the Facebook/network flow.
        try:
            src = (self.driver.page_source or "").lower()
        except Exception:
            src = ""
        if "oops" not in src and "connection error" not in src:
            return False
        try:
            self._find_clickable(self.OOPS_OK, timeout=3).click()
            return True
        except Exception:
            return False

    def has_basic_accessibility_labels(self) -> bool:
        src = self.driver.page_source or ""
        checks = ["Kantar Logo", "Connect with Facebook", "Email", "Password", "Login"]
        return all(token in src for token in checks if token)
