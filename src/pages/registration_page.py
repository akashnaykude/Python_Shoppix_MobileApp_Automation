import re
import time

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from src.pages.login_page import LoginPage
from src.pages.welcome_page import WelcomePage


class RegistrationPage:
    LOGO = (AppiumBy.XPATH, "//android.widget.ImageView[@content-desc='Kantar Logo']")
    HEADING = (AppiumBy.XPATH, "//android.widget.TextView[@text='Welcome to Shoppix!']")
    SUBTITLE = (
        AppiumBy.XPATH,
        "//android.widget.TextView[contains(@text, 'Start snapping receipts') and contains(@text, 'earning rewards')]",
    )
    BACK_BUTTON = (AppiumBy.XPATH, "//android.widget.ImageView[@content-desc='Back']")

    EMAIL_LABEL = (AppiumBy.XPATH, "//android.widget.TextView[@text='Email']")
    CREATE_PASSWORD_LABEL = (AppiumBy.XPATH, "//android.widget.TextView[@text='Create password']")
    CONFIRM_PASSWORD_LABEL = (AppiumBy.XPATH, "//android.widget.TextView[@text='Confirm Password']")
    REFERRAL_LABEL = (AppiumBy.XPATH, "//android.widget.TextView[@text='Have a referral code?']")

    EMAIL_INPUT = (AppiumBy.XPATH, "(//android.widget.EditText)[1]")
    CREATE_PASSWORD_INPUT = (AppiumBy.XPATH, "(//android.widget.EditText)[2]")
    CONFIRM_PASSWORD_INPUT = (AppiumBy.XPATH, "(//android.widget.EditText)[3]")
    REFERRAL_INPUT = (AppiumBy.XPATH, "(//android.widget.EditText)[4]")

    EMAIL_PLACEHOLDER = (AppiumBy.XPATH, "//android.widget.TextView[@text='Enter your email']")
    CREATE_PASSWORD_PLACEHOLDER = (AppiumBy.XPATH, "//android.widget.TextView[@text='Create your password']")
    CONFIRM_PASSWORD_PLACEHOLDER = (AppiumBy.XPATH, "//android.widget.TextView[@text='Confirm your password']")
    REFERRAL_PLACEHOLDER = (AppiumBy.XPATH, "//android.widget.TextView[@text='Enter referral code']")

    CREATE_PASSWORD_TOGGLE = (AppiumBy.XPATH, "(//android.widget.EditText)[2]//android.widget.Button")
    CONFIRM_PASSWORD_TOGGLE = (AppiumBy.XPATH, "(//android.widget.EditText)[3]//android.widget.Button")

    AGE_CHECKBOX = (AppiumBy.XPATH, "//android.widget.CheckBox")
    CONSENT_TEXT = (
        AppiumBy.XPATH,
        "//android.widget.TextView[contains(@text, 'Terms') and contains(@text, 'Privacy Policy')]",
    )

    CONTINUE_TEXT = (AppiumBy.XPATH, "//android.widget.TextView[@text='Continue']")
    CONTINUE_CTA = (
        AppiumBy.XPATH,
        "//android.widget.TextView[@text='Continue']/ancestor::android.view.View[@clickable='true'][1]",
    )
    CONTINUE_BUTTON = (AppiumBy.XPATH, "//android.widget.Button[ancestor::*[.//android.widget.TextView[@text='Continue']]]")

    SOCIAL_REG_TEXT = (AppiumBy.XPATH, "//android.widget.TextView[contains(@text, 'or register with')]")
    FACEBOOK_BUTTON = (
        AppiumBy.XPATH,
        "//android.widget.ImageView[@content-desc='Connect with Facebook' or @content-desc='Register with Facebook']",
    )

    TERMS_SCREEN_TITLE = (AppiumBy.XPATH, "//android.widget.TextView[@text='Terms and Conditions']")
    PRIVACY_SCREEN_TITLE = (AppiumBy.XPATH, "//android.widget.TextView[@text='Privacy Policy']")
    LEGAL_WEBVIEW = (AppiumBy.XPATH, "//android.webkit.WebView")

    PASSWORD_WEAK_ERROR = (AppiumBy.XPATH, "//android.widget.TextView[contains(@text, 'Please check your password')]")
    PASSWORD_POLICY_ERROR = (
        AppiumBy.XPATH,
        "//android.widget.TextView[contains(@text, 'at least 8 characters') or contains(@text, 'upper case')]",
    )
    PASSWORD_MISMATCH_ERROR = (
        AppiumBy.XPATH,
        "//android.widget.TextView[contains(@text, 'confirm password are different')]",
    )
    EMAIL_REQUIRED_ERROR = (AppiumBy.XPATH, "//android.widget.TextView[contains(@text, 'Please enter an email')]")
    EMAIL_INVALID_ERROR = (AppiumBy.XPATH, "//android.widget.TextView[contains(@text, 'valid email') or contains(@text, 'Invalid')]")

    CONSENT_REQUIRED_ERROR = (
        AppiumBy.XPATH,
        "//android.widget.TextView[contains(@text, 'Please confirm you are aged 18 or older')]",
    )

    OOPS_TITLE = (AppiumBy.XPATH, "//android.widget.TextView[@text='Oops']")
    ALREADY_REGISTERED_MESSAGE = (
        AppiumBy.XPATH,
        "//android.widget.TextView[contains(@text, 'already registered')]",
    )
    OOPS_OK_TEXT = (AppiumBy.XPATH, "//android.widget.TextView[@text='OK']")

    def __init__(self, driver):
        self.driver = driver
        self._last_accessibility_missing: list[str] = []

    def _find(self, locator, timeout: int = 15):
        return WebDriverWait(self.driver, timeout).until(ec.presence_of_element_located(locator))

    def _find_clickable(self, locator, timeout: int = 15):
        return WebDriverWait(self.driver, timeout).until(ec.element_to_be_clickable(locator))

    def _is_visible(self, locator, timeout: int = 6) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(ec.visibility_of_element_located(locator))
            return True
        except Exception:
            return False

    def _tap_xy(self, x: int, y: int):
        try:
            self.driver.execute_script("mobile: clickGesture", {"x": x, "y": y})
        except Exception:
            self.driver.tap([(x, y)])

    def _tap_element_center(self, elem):
        bounds = elem.get_attribute("bounds") or ""
        match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
        if not match:
            return False
        x1, y1, x2, y2 = map(int, match.groups())
        self._tap_xy((x1 + x2) // 2, (y1 + y2) // 2)
        return True

    def _dismiss_keyboard_if_needed(self):
        try:
            if hasattr(self.driver, "is_keyboard_shown") and self.driver.is_keyboard_shown():
                self.driver.hide_keyboard()
        except Exception:
            pass

    def _scroll_to_text(self, text: str):
        try:
            self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView(new UiSelector().textContains("{text}"))',
            )
        except Exception:
            pass

    def navigate_to_registration_if_needed(self):
        if self.is_registration_screen_visible(timeout=3):
            return

        welcome = WelcomePage(self.driver)
        if welcome.is_welcome_visible(timeout=3):
            welcome.tap_email_registration_icon()
            return

        login = LoginPage(self.driver)
        if login.is_login_screen_visible(timeout=3):
            login.tap_sign_up()
            return

        # Fallback: try back once, then attempt from welcome.
        try:
            self.driver.back()
        except Exception:
            pass

        if welcome.is_welcome_visible(timeout=3):
            welcome.tap_email_registration_icon()

    def is_registration_screen_visible(self, timeout: int = 10) -> bool:
        return self._is_visible(self.HEADING, timeout=timeout) and self._is_visible(self.EMAIL_LABEL, timeout=timeout)

    def reset_form(self):
        for locator in [self.EMAIL_INPUT, self.CREATE_PASSWORD_INPUT, self.CONFIRM_PASSWORD_INPUT, self.REFERRAL_INPUT]:
            try:
                self._find(locator, timeout=3).clear()
            except Exception:
                pass

    def is_logo_visible(self, timeout: int = 5) -> bool:
        return self._is_visible(self.LOGO, timeout=timeout)

    def is_heading_visible(self, timeout: int = 5) -> bool:
        return self._is_visible(self.HEADING, timeout=timeout)

    def is_subtitle_visible(self, timeout: int = 5) -> bool:
        return self._is_visible(self.SUBTITLE, timeout=timeout)

    def is_back_button_visible(self, timeout: int = 5) -> bool:
        return self._is_visible(self.BACK_BUTTON, timeout=timeout)

    def is_email_label_visible(self, timeout: int = 5) -> bool:
        return self._is_visible(self.EMAIL_LABEL, timeout=timeout)

    def is_email_placeholder_visible(self, timeout: int = 5) -> bool:
        return self._is_visible(self.EMAIL_PLACEHOLDER, timeout=timeout)

    def is_create_password_label_visible(self, timeout: int = 5) -> bool:
        return self._is_visible(self.CREATE_PASSWORD_LABEL, timeout=timeout)

    def is_create_password_placeholder_visible(self, timeout: int = 5) -> bool:
        return self._is_visible(self.CREATE_PASSWORD_PLACEHOLDER, timeout=timeout)

    def is_confirm_password_label_visible(self, timeout: int = 5) -> bool:
        return self._is_visible(self.CONFIRM_PASSWORD_LABEL, timeout=timeout)

    def is_confirm_password_placeholder_visible(self, timeout: int = 5) -> bool:
        return self._is_visible(self.CONFIRM_PASSWORD_PLACEHOLDER, timeout=timeout)

    def is_referral_label_visible(self, timeout: int = 5) -> bool:
        self._scroll_to_text("Have a referral code")
        return self._is_visible(self.REFERRAL_LABEL, timeout=timeout)

    def is_referral_placeholder_visible(self, timeout: int = 5) -> bool:
        self._scroll_to_text("Have a referral code")
        return self._is_visible(self.REFERRAL_PLACEHOLDER, timeout=timeout)

    def is_age_checkbox_visible(self, timeout: int = 5) -> bool:
        self._scroll_to_text("I confirm that I am 18 years")
        return self._is_visible(self.AGE_CHECKBOX, timeout=timeout)

    def is_continue_button_visible(self, timeout: int = 5) -> bool:
        self._scroll_to_text("Continue")
        return self._is_visible(self.CONTINUE_TEXT, timeout=timeout)

    def is_social_registration_text_visible(self, timeout: int = 5) -> bool:
        self._scroll_to_text("or register with")
        return self._is_visible(self.SOCIAL_REG_TEXT, timeout=timeout)

    def is_facebook_registration_visible(self, timeout: int = 5) -> bool:
        self._scroll_to_text("or register with")
        return self._is_visible(self.FACEBOOK_BUTTON, timeout=timeout)

    def enter_email(self, email: str):
        elem = self._find(self.EMAIL_INPUT, timeout=8)
        elem.clear()
        elem.send_keys(email)

    def enter_create_password(self, password: str):
        elem = self._find(self.CREATE_PASSWORD_INPUT, timeout=8)
        elem.clear()
        elem.send_keys(password)

    def enter_confirm_password(self, password: str):
        elem = self._find(self.CONFIRM_PASSWORD_INPUT, timeout=8)
        elem.clear()
        elem.send_keys(password)

    def enter_referral_code(self, referral_code: str):
        self._scroll_to_text("Have a referral code")
        elem = self._find(self.REFERRAL_INPUT, timeout=8)
        elem.clear()
        elem.send_keys(referral_code)

    def get_email_value(self) -> str:
        return (self._find(self.EMAIL_INPUT, timeout=4).get_attribute("text") or "").strip()

    def get_referral_value(self) -> str:
        return (self._find(self.REFERRAL_INPUT, timeout=4).get_attribute("text") or "").strip()

    def _is_password_masked(self, locator) -> bool:
        try:
            elem = self._find(locator, timeout=4)
            attr_password = str(elem.get_attribute("password")).lower() == "true"
            text_value = elem.get_attribute("text") or ""
            return attr_password or ("•" in text_value)
        except Exception:
            return False

    def is_create_password_masked(self) -> bool:
        return self._is_password_masked(self.CREATE_PASSWORD_INPUT)

    def is_confirm_password_masked(self) -> bool:
        return self._is_password_masked(self.CONFIRM_PASSWORD_INPUT)

    def _toggle_password(self, locator):
        self._dismiss_keyboard_if_needed()
        try:
            self._find_clickable(locator, timeout=4).click()
        except Exception:
            self._find(locator, timeout=4).click()

    def tap_create_password_toggle(self):
        self._toggle_password(self.CREATE_PASSWORD_TOGGLE)

    def tap_confirm_password_toggle(self):
        self._toggle_password(self.CONFIRM_PASSWORD_TOGGLE)

    def _is_password_visible_as(self, locator, expected: str) -> bool:
        try:
            elem = self._find(locator, timeout=4)
            is_visible_attr = str(elem.get_attribute("password")).lower() == "false"
            value = (elem.get_attribute("text") or "").strip()
            return is_visible_attr and value == expected
        except Exception:
            return False

    def _is_password_hidden_from(self, locator, plain: str) -> bool:
        try:
            elem = self._find(locator, timeout=4)
            is_masked_attr = str(elem.get_attribute("password")).lower() == "true"
            value = (elem.get_attribute("text") or "").strip()
            return is_masked_attr or value != plain
        except Exception:
            return False

    def wait_until_create_password_visible_as(self, expected: str, timeout: float = 2.5) -> bool:
        end = time.time() + timeout
        while time.time() < end:
            if self._is_password_visible_as(self.CREATE_PASSWORD_INPUT, expected):
                return True
            time.sleep(0.2)
        return False

    def wait_until_create_password_hidden_from(self, plain: str, timeout: float = 2.5) -> bool:
        end = time.time() + timeout
        while time.time() < end:
            if self._is_password_hidden_from(self.CREATE_PASSWORD_INPUT, plain):
                return True
            time.sleep(0.2)
        return False

    def wait_until_confirm_password_visible_as(self, expected: str, timeout: float = 2.5) -> bool:
        end = time.time() + timeout
        while time.time() < end:
            if self._is_password_visible_as(self.CONFIRM_PASSWORD_INPUT, expected):
                return True
            time.sleep(0.2)
        return False

    def wait_until_confirm_password_hidden_from(self, plain: str, timeout: float = 2.5) -> bool:
        end = time.time() + timeout
        while time.time() < end:
            if self._is_password_hidden_from(self.CONFIRM_PASSWORD_INPUT, plain):
                return True
            time.sleep(0.2)
        return False

    def tap_age_checkbox(self):
        self._scroll_to_text("I confirm that I am 18 years")

        # Fast path for native checkbox accessibility exposure.
        try:
            self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().className("android.widget.CheckBox").instance(0)',
            ).click()
            return
        except Exception:
            pass

        elem = None
        try:
            self._find_clickable(self.AGE_CHECKBOX, timeout=5).click()
            return
        except Exception:
            try:
                elem = self._find(self.AGE_CHECKBOX, timeout=3)
            except Exception:
                elem = None

        if elem is not None:
            match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", elem.get_attribute("bounds") or "")
            if match:
                x1, y1, x2, y2 = map(int, match.groups())
                self._tap_xy((x1 + x2) // 2, (y1 + y2) // 2)
                return

        # Fallback for builds where checkbox is rendered but not exposed as clickable.
        consent = self._find(self.CONSENT_TEXT, timeout=5)
        match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", consent.get_attribute("bounds") or "")
        if not match:
            raise AssertionError("Could not resolve consent bounds for checkbox fallback tap")

        x1, y1, _, y2 = map(int, match.groups())
        x = max(20, x1 - 80)
        y = (y1 + y2) // 2
        self._tap_xy(x, y)
        return

    def tap_age_checkbox_by_relative_layout(self):
        self._scroll_to_text("Continue")
        try:
            continue_elem = self._find(self.CONTINUE_TEXT, timeout=4)
            bounds = continue_elem.get_attribute("bounds") or ""
            match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
            if not match:
                return
            x1, y1, _, _ = map(int, match.groups())
            self._tap_xy(max(40, x1 - 350), max(120, y1 - 170))
        except Exception:
            pass

    def is_age_checkbox_selected(self) -> bool:
        try:
            self._scroll_to_text("I confirm that I am 18 years")
            elem = self._find(self.AGE_CHECKBOX, timeout=5)
            checked = str(elem.get_attribute("checked")).lower()
            if checked in {"true", "false"}:
                return checked == "true"
        except Exception:
            pass

        # Fallback when the element attribute is not exposed consistently.
        src = self.driver.page_source or ""
        match = re.search(r'class="android\.widget\.CheckBox"[^>]*checked="(true|false)"', src)
        if match:
            return match.group(1) == "true"

        return False

    def wait_until_age_checkbox_state(self, expected_selected: bool, timeout: float = 2.5) -> bool:
        end = time.time() + timeout
        while time.time() < end:
            if self.is_age_checkbox_selected() == expected_selected:
                return True
            time.sleep(0.2)
        return False

    def set_age_checkbox_state(self, expected_selected: bool, timeout: float = 6.0):
        end = time.time() + timeout
        while time.time() < end:
            current = self.is_age_checkbox_selected()
            if current == expected_selected:
                return
            self.tap_age_checkbox()
            time.sleep(0.3)

            current = self.is_age_checkbox_selected()
            if current == expected_selected:
                return

            self.tap_age_checkbox_by_relative_layout()
            time.sleep(0.3)

        # Some builds do not expose checkbox state reliably; keep this best-effort.
        if expected_selected:
            self.tap_age_checkbox()

    def _find_consent_element(self, timeout: int = 6):
        locators = [
            self.CONSENT_TEXT,
            (AppiumBy.XPATH, "//android.widget.TextView[contains(@text, 'agree to the')]"),
            (AppiumBy.XPATH, "//android.widget.TextView[contains(@text, 'Privacy Policy')]"),
            (AppiumBy.XPATH, "//android.widget.TextView[contains(@text, 'Terms')]"),
        ]

        for locator in locators:
            try:
                return self._find(locator, timeout=timeout)
            except Exception:
                pass

        # Final fallback: scroll directly to the combined consent sentence.
        try:
            return self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView(new UiSelector().textContains("Privacy Policy"))',
            )
        except Exception:
            pass

        try:
            return self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView(new UiSelector().textContains("agree to the"))',
            )
        except Exception:
            return None

    def _tap_link_in_consent_text(self, link: str):
        self._scroll_to_text("Terms")
        text_hint = "Terms" if link == "terms" else "Privacy"
        expected_visible = self.is_terms_screen_visible if link == "terms" else self.is_privacy_screen_visible
        opposite_visible = self.is_privacy_screen_visible if link == "terms" else self.is_terms_screen_visible

        # First try: find the text element (even if not clickable) and tap its center.
        text_presence_locators = [
            (AppiumBy.XPATH, f"//android.widget.TextView[contains(@text, '{text_hint}')]"),
            (AppiumBy.XPATH, f"//*[contains(@text, '{text_hint}')]"),
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{text_hint}")'),
        ]
        for locator in text_presence_locators:
            try:
                elem = self._find(locator, timeout=2)
                if self._tap_element_center(elem):
                    if expected_visible(timeout=3):
                        return
                    if opposite_visible(timeout=1.2):
                        try:
                            self.driver.back()
                        except Exception:
                            pass
            except Exception:
                pass

        # Fast path for builds where legal links are separately clickable text spans.
        text_locators = [
            (AppiumBy.XPATH, f"//android.widget.TextView[contains(@text, '{text_hint}')]"),
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{text_hint}")'),
        ]
        for locator in text_locators:
            try:
                self._find_clickable(locator, timeout=2).click()
                if expected_visible(timeout=3):
                    return
                if opposite_visible(timeout=1.2):
                    try:
                        self.driver.back()
                    except Exception:
                        pass
                try:
                    self.driver.back()
                except Exception:
                    pass
            except Exception:
                pass

        consent = self._find_consent_element(timeout=8)
        if consent is None:
            # Fallback anchored to age-checkbox row (this row is available in current builds).
            try:
                checkbox = self._find(self.AGE_CHECKBOX, timeout=4)
                match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", checkbox.get_attribute("bounds") or "")
                if match:
                    _, y1, x2, y2 = map(int, match.groups())
                    y_candidates = [((y1 + y2) // 2) - 14, ((y1 + y2) // 2) + 26]
                    x_candidates = [x2 + 300, x2 + 460] if link == "terms" else [x2 + 560, x2 + 680]
                    for y in y_candidates:
                        for x in x_candidates:
                            self._tap_xy(x, y)
                            if expected_visible(timeout=3):
                                return
            except Exception:
                pass

            # Last-chance fallback using viewport-relative coordinates near consent links.
            try:
                continue_elem = self._find(self.CONTINUE_TEXT, timeout=4)
                bounds = continue_elem.get_attribute("bounds") or ""
                match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
                if match:
                    x1, y1, x2, _ = map(int, match.groups())
                    width = x2 - x1
                    y_candidates = [max(120, y1 - 185), max(120, y1 - 135)]
                    x_ratio = 0.58 if link == "terms" else 0.82
                    for y in y_candidates:
                        x = x1 + int(width * x_ratio)
                        self._tap_xy(x, y)
                        if expected_visible(timeout=3):
                            return
            except Exception:
                pass

            rect = self.driver.get_window_rect()
            y = int(rect["height"] * 0.76)
            x = int(rect["width"] * (0.62 if link == "terms" else 0.84))
            self._tap_xy(x, y)
            if expected_visible(timeout=3):
                return
            raise AssertionError("Could not find consent text container for legal link tap")

        match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", consent.get_attribute("bounds") or "")
        if not match:
            raise AssertionError("Could not resolve consent text bounds for legal link tap")

        x1, y1, x2, y2 = map(int, match.groups())
        width = x2 - x1
        height = y2 - y1

        if link == "terms":
            x_ratios = [0.66, 0.74, 0.60]
        else:
            x_ratios = [0.87, 0.80, 0.92]

        y_ratios = [0.45, 0.70]

        for y_ratio in y_ratios:
            for x_ratio in x_ratios:
                x = x1 + int(width * x_ratio)
                y = y1 + int(height * y_ratio)
                self._tap_xy(x, y)
                if expected_visible(timeout=3):
                    return

        raise AssertionError(f"Could not open {text_hint} screen from consent links")

    def tap_terms_link(self):
        self._tap_link_in_consent_text("terms")

    def scroll_to_terms_and_conditions_link(self):
        self._reveal_consent_fully()

    def _reveal_consent_fully(self):
        # The consent row sits just above Continue; scroll to content below it so the
        # full multi-line consent text is on-screen (not clipped at the scroll edge).
        if self._consent_fully_visible():
            return
        for target in ["or register with", "Continue", "Privacy Policy"]:
            try:
                self.driver.find_element(
                    AppiumBy.ANDROID_UIAUTOMATOR,
                    f'new UiScrollable(new UiSelector().scrollable(true))'
                    f'.scrollIntoView(new UiSelector().textContains("{target}"))',
                )
                return
            except Exception:
                continue

    def _consent_fully_visible(self) -> bool:
        # True when the consent text is on-screen with its full (unclipped) height.
        try:
            els = self.driver.find_elements(*self.CONSENT_TEXT)
        except Exception:
            return False
        if not els:
            return False
        m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", els[0].get_attribute("bounds") or "")
        if not m:
            return False
        _, y1, _, y2 = map(int, m.groups())
        return (y2 - y1) >= 60

    def _detect_legal_screen(self, timeout: float = 2.5) -> str:
        # Fast native-title probe: returns 'terms', 'privacy', or '' without blocking waits.
        end = time.time() + timeout
        while time.time() < end:
            try:
                if self.driver.find_elements(*self.TERMS_SCREEN_TITLE):
                    return "terms"
                if self.driver.find_elements(*self.PRIVACY_SCREEN_TITLE):
                    return "privacy"
            except Exception:
                pass
            time.sleep(0.2)
        return ""

    def _back_to_registration(self, timeout: int = 4) -> bool:
        try:
            self.driver.back()
        except Exception:
            return False
        return self.is_registration_screen_visible(timeout=timeout)

    def tap_terms_and_conditions_text_simple(self):
        # Strict path: tap exactly on the "Terms & Conditions" link, never on Privacy.
        self._reveal_consent_fully()

        consent = self._find_consent_element(timeout=4)
        if consent is None:
            return False

        text_value = (consent.get_attribute("text") or "").strip()
        bounds = consent.get_attribute("bounds") or ""
        match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
        if not match or not text_value or "terms" not in text_value.lower():
            return False

        x1, y1, x2, y2 = map(int, match.groups())
        width = x2 - x1
        height = y2 - y1

        # Terms link spans "Terms &" (line 2 right) + "Conditions" (line 3 left); Privacy
        # sits on line 3 right, so line 3 left is the safe Terms-only target.
        line_count = max(1, round(height / 66))
        if line_count >= 3:
            terms_points = [
                (0.17, 0.83),  # "Conditions" - line 3 left
                (0.27, 0.83),  # "Conditions" - slight right
                (0.82, 0.50),  # "Terms &" - end of line 2
                (0.72, 0.50),  # "Terms &" - slight left
            ]
        elif line_count == 2:
            terms_points = [
                (0.12, 0.75),  # "Conditions" wrapped to line 2 left
                (0.80, 0.25),  # "Terms &" end of line 1
                (0.70, 0.25),
            ]
        else:
            terms_points = [
                (0.62, 0.5),
                (0.70, 0.5),
            ]

        for x_ratio, y_ratio in terms_points:
            x = x1 + int(width * x_ratio)
            y = y1 + int(height * y_ratio)
            self._tap_xy(x, y)
            screen = self._detect_legal_screen(timeout=2.0)
            if screen == "terms":
                return True
            if screen == "privacy":
                # Wrong span hit; return to registration and try the next Terms point.
                self._back_to_registration(timeout=4)
                self._reveal_consent_fully()

        return False

    def tap_terms_and_conditions_hotspot(self):
        # Secondary simple tap: Terms zone of consent line just above Continue.
        self._scroll_to_text("Continue")
        try:
            continue_elem = self._find(self.CONTINUE_TEXT, timeout=2)
            bounds = continue_elem.get_attribute("bounds") or ""
            match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
            if match:
                x1, y1, x2, _ = map(int, match.groups())
                width = x2 - x1
                self._tap_xy(x1 + int(width * 0.48), max(120, y1 - 145))
                return
        except Exception:
            pass

        rect = self.driver.get_window_rect()
        self._tap_xy(int(rect.get("width", 1080) * 0.62), int(rect.get("height", 2376) * 0.67))

    def scroll_to_privacy_policy_link(self):
        self._reveal_consent_fully()

    def tap_privacy_policy_text_simple(self):
        # Strict path: tap exactly on the "Privacy Policy" link, never on Terms.
        self._reveal_consent_fully()

        consent = self._find_consent_element(timeout=4)
        if consent is None:
            return False

        text_value = (consent.get_attribute("text") or "").strip()
        bounds = consent.get_attribute("bounds") or ""
        match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
        if not match or not text_value or "privacy policy" not in text_value.lower():
            return False

        x1, y1, x2, y2 = map(int, match.groups())
        width = x2 - x1
        height = y2 - y1

        # "Privacy Policy" is the trailing span: line 3 right on a 3-line wrap.
        # Its character center maps to ~0.74 of the consent width (avoid < 0.52 to not hit Terms).
        line_count = max(1, round(height / 66))
        if line_count >= 3:
            privacy_points = [
                (0.74, 0.83),  # "Privacy Policy" center - line 3
                (0.68, 0.83),
                (0.80, 0.83),
                (0.60, 0.83),
            ]
        elif line_count == 2:
            privacy_points = [
                (0.74, 0.75),
                (0.68, 0.75),
                (0.82, 0.75),
            ]
        else:
            privacy_points = [
                (0.80, 0.5),
                (0.72, 0.5),
            ]

        for x_ratio, y_ratio in privacy_points:
            x = x1 + int(width * x_ratio)
            y = y1 + int(height * y_ratio)
            self._tap_xy(x, y)
            screen = self._detect_legal_screen(timeout=2.0)
            if screen == "privacy":
                return True
            if screen == "terms":
                # Wrong span hit; return to registration and try the next Privacy point.
                self._back_to_registration(timeout=4)
                self._reveal_consent_fully()

        return False

    def tap_privacy_policy_hotspot(self):
        # Secondary simple tap: right side of consent line just above Continue.
        self._scroll_to_text("Continue")
        try:
            continue_elem = self._find(self.CONTINUE_TEXT, timeout=2)
            bounds = continue_elem.get_attribute("bounds") or ""
            match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
            if match:
                x1, y1, x2, _ = map(int, match.groups())
                width = x2 - x1
                self._tap_xy(x1 + int(width * 0.82), max(120, y1 - 145))
                return
        except Exception:
            pass

        rect = self.driver.get_window_rect()
        self._tap_xy(int(rect.get("width", 1080) * 0.82), int(rect.get("height", 2376) * 0.67))


    def is_terms_screen_visible(self, timeout: int = 8) -> bool:
        return self._is_visible(self.TERMS_SCREEN_TITLE, timeout=timeout) and self._is_visible(self.LEGAL_WEBVIEW, timeout=timeout)

    def is_privacy_screen_visible(self, timeout: int = 8) -> bool:
        return self._is_visible(self.PRIVACY_SCREEN_TITLE, timeout=timeout) and self._is_visible(self.LEGAL_WEBVIEW, timeout=timeout)

    def tap_continue(self):
        self._dismiss_keyboard_if_needed()
        self._scroll_to_text("Continue")
        try:
            self._find_clickable(self.CONTINUE_CTA, timeout=5).click()
        except Exception:
            self._find_clickable(self.CONTINUE_TEXT, timeout=5).click()

    def is_continue_button_enabled(self) -> bool:
        self._scroll_to_text("Continue")
        try:
            button = self._find(self.CONTINUE_BUTTON, timeout=3)
            button_enabled = str(button.get_attribute("enabled")).lower() == "true"
            button_clickable = str(button.get_attribute("clickable")).lower() == "true"
            if button_enabled and button_clickable:
                return True
        except Exception:
            pass

        try:
            cta = self._find(self.CONTINUE_CTA, timeout=3)
            return str(cta.get_attribute("enabled")).lower() == "true"
        except Exception:
            return False

    def tap_facebook_registration(self):
        self._scroll_to_text("or register with")
        self._find_clickable(self.FACEBOOK_BUTTON, timeout=8).click()

    def is_email_format_error_visible(self) -> bool:
        if self._is_visible(self.EMAIL_INVALID_ERROR, timeout=2):
            return True
        src = (self.driver.page_source or "").lower()
        return "invalid" in src and "email" in src

    def is_email_required_error_visible(self) -> bool:
        if self._is_visible(self.EMAIL_REQUIRED_ERROR, timeout=2):
            return True
        src = (self.driver.page_source or "").lower()
        return "please enter an email" in src or "please enter email" in src

    def is_password_strength_error_visible(self) -> bool:
        if self._is_visible(self.PASSWORD_WEAK_ERROR, timeout=2) or self._is_visible(self.PASSWORD_POLICY_ERROR, timeout=2):
            return True
        src = (self.driver.page_source or "").lower()
        return "please check your password" in src or "at least 8 characters" in src

    def is_password_mismatch_error_visible(self) -> bool:
        if self._is_visible(self.PASSWORD_MISMATCH_ERROR, timeout=2):
            return True
        src = (self.driver.page_source or "").lower()
        return "confirm password are different" in src

    def is_create_password_required_error_visible(self) -> bool:
        src = (self.driver.page_source or "").lower()
        if "please check your password" in src:
            val = (self._find(self.CREATE_PASSWORD_INPUT, timeout=3).get_attribute("text") or "").strip()
            return val == ""
        return False

    def is_confirm_password_required_error_visible(self) -> bool:
        src = (self.driver.page_source or "").lower()
        if "confirm password" in src and "different" in src:
            return False
        # Some builds only set content-invalid on the field.
        try:
            elem = self._find(self.CONFIRM_PASSWORD_INPUT, timeout=3)
            invalid = str(elem.get_attribute("contentInvalid")).lower() == "true"
            val = (elem.get_attribute("text") or "").strip()
            return invalid and val == ""
        except Exception:
            return False

    def is_referral_optional(self) -> bool:
        src = (self.driver.page_source or "").lower()
        return "referral" in src and "invalid referral" not in src and "please enter referral" not in src

    def is_consent_required_error_visible(self) -> bool:
        if self._is_visible(self.CONSENT_REQUIRED_ERROR, timeout=2):
            return True
        src = (self.driver.page_source or "").lower()
        return "please confirm you are aged 18 or older" in src

    def is_referral_validation_error_visible(self) -> bool:
        src = (self.driver.page_source or "").lower()
        return "invalid referral" in src or "referral code" in src and "invalid" in src

    def is_terms_and_conditions_text_visible(self) -> bool:
        # page_source escapes '&' to '&amp;', so match the element's unescaped text.
        self._reveal_consent_fully()
        consent = self._find_consent_element(timeout=4)
        text = (consent.get_attribute("text") or "") if consent is not None else ""
        return "Terms & Conditions" in text or "Terms and Conditions" in text

    def is_privacy_policy_text_visible(self) -> bool:
        self._reveal_consent_fully()
        consent = self._find_consent_element(timeout=4)
        if consent is not None and "Privacy Policy" in (consent.get_attribute("text") or ""):
            return True
        return "Privacy Policy" in (self.driver.page_source or "")

    def is_already_registered_alert_visible(self) -> bool:
        return self._is_visible(self.OOPS_TITLE, timeout=3) and self._is_visible(self.ALREADY_REGISTERED_MESSAGE, timeout=3)

    def dismiss_already_registered_alert(self):
        self._find_clickable(self.OOPS_OK_TEXT, timeout=5).click()

    def is_facebook_auth_flow_displayed(self) -> bool:
        if self.is_already_registered_alert_visible():
            return True
        src = (self.driver.page_source or "").lower()
        if "facebook" in src and ("continue" in src or "log in" in src):
            return True
        return not self.is_registration_screen_visible(timeout=1)

    def has_basic_accessibility_labels(self) -> bool:
        self._scroll_to_text("Welcome to Shoppix")
        checks: list[tuple[str, bool]] = [
            ("back_button", self.is_back_button_visible(timeout=3)),
            ("logo", self.is_logo_visible(timeout=3)),
            ("heading", self.is_heading_visible(timeout=3)),
            ("email_label_or_placeholder", self.is_email_label_visible(timeout=3) or self.is_email_placeholder_visible(timeout=3)),
            (
                "create_password_label_or_placeholder",
                self.is_create_password_label_visible(timeout=3) or self.is_create_password_placeholder_visible(timeout=3),
            ),
            (
                "confirm_password_label_or_placeholder",
                self.is_confirm_password_label_visible(timeout=3) or self.is_confirm_password_placeholder_visible(timeout=3),
            ),
        ]

        self._scroll_to_text("Have a referral code")
        checks.extend(
            [
                ("referral_label", self.is_referral_label_visible(timeout=3)),
                ("referral_placeholder", self.is_referral_placeholder_visible(timeout=3)),
            ]
        )

        self._scroll_to_text("Continue")
        checks.extend(
            [
                ("age_checkbox", self.is_age_checkbox_visible(timeout=3)),
                ("terms_text", self._is_visible(self.CONSENT_TEXT, timeout=3) or self.is_terms_and_conditions_text_visible()),
                ("privacy_text", self.is_privacy_policy_text_visible()),
                ("continue_button", self.is_continue_button_visible(timeout=3)),
                ("social_registration_text", self.is_social_registration_text_visible(timeout=3)),
                ("facebook_registration", self.is_facebook_registration_visible(timeout=3)),
            ]
        )

        self._last_accessibility_missing = [name for name, ok in checks if not ok]
        return not self._last_accessibility_missing

    def last_accessibility_missing(self) -> list[str]:
        return list(self._last_accessibility_missing)

    def restore_registration_top(self, timeout: int = 5) -> bool:
        if self.is_heading_visible(timeout=1.2):
            return True

        try:
            self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiScrollable(new UiSelector().scrollable(true)).scrollToBeginning(10)',
            )
        except Exception:
            pass

        if self.is_heading_visible(timeout=1.8):
            return True

        rect = self.driver.get_window_rect()
        left = int(rect.get("x", 0) + rect.get("width", 1080) * 0.08)
        top = int(rect.get("y", 0) + rect.get("height", 2376) * 0.24)
        width = int(rect.get("width", 1080) * 0.84)
        height = int(rect.get("height", 2376) * 0.56)

        # Move content toward the top of the form when scrollToBeginning is ineffective.
        for _ in range(6):
            self.driver.execute_script(
                "mobile: scrollGesture",
                {
                    "left": left,
                    "top": top,
                    "width": width,
                    "height": height,
                    "direction": "down",
                    "percent": 0.9,
                },
            )
            if self.is_heading_visible(timeout=1.2):
                return True

        self._scroll_to_text("Welcome to Shoppix")
        return self.is_heading_visible(timeout=timeout)

    def is_core_content_visible(self) -> bool:
        top_ok = self.is_heading_visible(timeout=5) and self.is_email_label_visible(timeout=5)
        bottom_ok = self.is_continue_button_visible(timeout=5)
        return top_ok and bottom_ok
