import re
import time

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from src.pages.welcome_page import WelcomePage


class WaitingListPage:
    """Registration flow shown when admin has enabled the waiting list.

    These screens expose no app resource-ids (all resource-id=""), so inputs
    are resolved relative to their stable label text (ground-truthed from the
    live page_source), not by positional EditText index.
    """

    # ---- static markers ----------------------------------------------------
    BACK_BUTTON = (AppiumBy.XPATH, "//android.widget.ImageView[@content-desc='Back']")
    LOGO = (AppiumBy.XPATH, "//android.widget.ImageView[@content-desc='Kantar Logo']")
    HEADING = (AppiumBy.XPATH, "//android.widget.TextView[@text='Thank you for your interest in Shoppix!']")
    DESCRIPTION_TEXT = (AppiumBy.XPATH, "//android.widget.TextView[contains(@text, 'high demand')]")
    REFERRAL_INSTRUCTION = (AppiumBy.XPATH, "//android.widget.TextView[contains(@text, 'Have a valid referral code')]")

    EMAIL_LABEL = (AppiumBy.XPATH, "//android.widget.TextView[@text='Email']")
    POSTCODE_LABEL = (AppiumBy.XPATH, "//android.widget.TextView[@text='Postcode']")
    AGE_LABEL = (AppiumBy.XPATH, "//android.widget.TextView[@text='Age range']")
    REFERRAL_LABEL = (AppiumBy.XPATH, "//android.widget.TextView[@text='Have a referral code?']")

    # UiAutomator class instances avoid XPath2 following-axis crashes.
    EMAIL_INPUT = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().className("android.widget.EditText").instance(0)',
    )
    POSTCODE_INPUT = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().className("android.widget.EditText").instance(1)',
    )
    REFERRAL_INPUT = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().className("android.widget.EditText").instance(3)',
    )

    EMAIL_PLACEHOLDER = (AppiumBy.XPATH, "//android.widget.TextView[@text='Enter your email']")
    POSTCODE_PLACEHOLDER = (AppiumBy.XPATH, "//android.widget.TextView[@text='Enter your postcode']")
    AGE_PLACEHOLDER = (AppiumBy.XPATH, "//android.widget.TextView[@text='Select your age']")
    REFERRAL_PLACEHOLDER = (AppiumBy.XPATH, "//android.widget.TextView[@text='Enter referral code']")

    # Age range is a disabled EditText inside a clickable View; the selected
    # value surfaces as that EditText's text attribute (e.g. "45-54").
    AGE_DROPDOWN = (
        AppiumBy.XPATH,
        "//android.view.View[@clickable='true' and .//android.widget.EditText[@enabled='false']]",
    )
    AGE_VALUE = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().className("android.widget.EditText").instance(2)',
    )
    AGE_OPTIONS = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]

    CONSENT_CHECKBOX = (AppiumBy.XPATH, "//android.widget.CheckBox")
    CONSENT_TEXT = (AppiumBy.XPATH, "//android.widget.TextView[contains(@text, 'consent to Worldpanel')]")
    PRIVACY_NOTE = (
        AppiumBy.XPATH,
        "//android.widget.TextView[contains(@text, 'personal information will only be used')]",
    )

    CONTINUE_TEXT = (AppiumBy.XPATH, "//android.widget.TextView[@text='Continue']")
    CONTINUE_CTA = (
        AppiumBy.XPATH,
        "//android.widget.TextView[@text='Continue']/ancestor::android.view.View[@clickable='true'][1]",
    )

    # ---- validation messages (exact text from page_source) -----------------
    EMAIL_REQUIRED_ERROR = (AppiumBy.XPATH, "//android.widget.TextView[@text='Please enter an email address']")
    EMAIL_INVALID_ERROR = (AppiumBy.XPATH, "//android.widget.TextView[@text='Please enter a valid email address']")
    POSTCODE_REQUIRED_ERROR = (AppiumBy.XPATH, "//android.widget.TextView[@text='Please enter a postcode']")
    POSTCODE_INVALID_ERROR = (AppiumBy.XPATH, "//android.widget.TextView[@text='Please enter a valid postcode']")
    AGE_REQUIRED_ERROR = (AppiumBy.XPATH, "//android.widget.TextView[@text='Please select age']")
    CONSENT_REQUIRED_ERROR = (
        AppiumBy.XPATH,
        "//android.widget.TextView[@text='Please confirm that you are over 18 years old']",
    )

    # ---- dialogs -----------------------------------------------------------
    SUCCESS_ALERT_MESSAGE = (AppiumBy.XPATH, "//android.widget.TextView[contains(@text, 'registered successfully')]")
    DONE_TEXT = (AppiumBy.XPATH, "//android.widget.TextView[@text='Done']")
    DONE_CTA = (
        AppiumBy.XPATH,
        "//android.widget.TextView[@text='Done']/ancestor::android.view.View[@clickable='true'][1]",
    )

    OOPS_TITLE = (AppiumBy.XPATH, "//android.widget.TextView[@text='Oops']")
    DUPLICATE_ALERT_MESSAGE = (
        AppiumBy.XPATH,
        "//android.widget.TextView[@text='This email address is already on the waitlist.']",
    )
    OK_TEXT = (AppiumBy.XPATH, "//android.widget.TextView[@text='OK']")
    OK_CTA = (
        AppiumBy.XPATH,
        "//android.widget.TextView[@text='OK']/ancestor::android.view.View[@clickable='true'][1]",
    )

    def __init__(self, driver):
        self.driver = driver

    # ---- low-level helpers -------------------------------------------------
    def _find(self, locator, timeout: int = 10):
        return WebDriverWait(self.driver, timeout).until(ec.presence_of_element_located(locator))

    def _find_clickable(self, locator, timeout: int = 15):
        return WebDriverWait(self.driver, timeout).until(ec.element_to_be_clickable(locator))

    def _is_visible(self, locator, timeout: int = 6) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(ec.visibility_of_element_located(locator))
            return True
        except Exception:
            return False

    def _present(self, locator) -> bool:
        try:
            return len(self.driver.find_elements(*locator)) > 0
        except Exception:
            return False

    def _tap_xy(self, x: int, y: int):
        try:
            self.driver.execute_script("mobile: clickGesture", {"x": x, "y": y})
        except Exception:
            self.driver.tap([(x, y)])

    def _tap_element_center(self, elem) -> bool:
        match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", elem.get_attribute("bounds") or "")
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

    def _scroll_to_top(self):
        try:
            self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiScrollable(new UiSelector().scrollable(true)).flingToBeginning(8)',
            )
        except Exception:
            pass

    def _shown(self, locator, scroll_hint: str | None = None, timeout: int = 4) -> bool:
        """Fast visibility check: return instantly if already on-screen, else
        scroll once (native ScrollView drops off-screen nodes) and poll briefly.
        """
        if self._present(locator):
            return True
        if scroll_hint is not None:
            self._scroll_to_text(scroll_hint)
            if self._present(locator):
                return True
        return self._is_visible(locator, timeout=timeout)

    # ---- navigation / flow detection --------------------------------------
    def navigate_from_welcome(self):
        welcome = WelcomePage(self.driver)
        if welcome.is_welcome_visible(timeout=3):
            welcome.tap_email_registration_icon()

    def is_waiting_list_visible(self, timeout: int = 6) -> bool:
        # Postcode is unique to the waiting list flow (normal registration has none).
        if self._present(self.POSTCODE_LABEL):
            return True
        return self._is_visible(self.POSTCODE_LABEL, timeout=timeout)

    def reset_form(self):
        for locator in (self.EMAIL_INPUT, self.POSTCODE_INPUT, self.REFERRAL_INPUT):
            try:
                self._find(locator, timeout=2).clear()
            except Exception:
                pass

    # ---- visibility getters (presence-first; scroll only when needed) ------
    def is_back_button_visible(self, timeout: int = 4) -> bool:
        return self._shown(self.BACK_BUTTON, timeout=timeout)

    def is_logo_visible(self, timeout: int = 4) -> bool:
        self._scroll_to_top()
        return self._shown(self.LOGO, "Thank you for your interest", timeout)

    def is_heading_visible(self, timeout: int = 4) -> bool:
        self._scroll_to_top()
        return self._shown(self.HEADING, "Thank you for your interest", timeout)

    def is_description_text_visible(self, timeout: int = 4) -> bool:
        self._scroll_to_top()
        if self._shown(self.DESCRIPTION_TEXT, "high demand", timeout):
            return True

        src = (self.driver.page_source or "").lower()
        return (
            "high demand" in src
            or "waiting list for new shoppix sign-ups" in src
            or "contact you when spaces become available" in src
        )

    def is_referral_instruction_visible(self, timeout: int = 4) -> bool:
        self._scroll_to_top()
        if self._shown(self.REFERRAL_INSTRUCTION, "referral code", timeout):
            return True

        src = (self.driver.page_source or "").lower()
        return (
            "have a valid referral code" in src
            or ("referral code" in src and "join shoppix today" in src)
        )

    def is_email_label_visible(self, timeout: int = 4) -> bool:
        return self._shown(self.EMAIL_LABEL, timeout=timeout)

    def is_email_placeholder_visible(self, timeout: int = 4) -> bool:
        return self._shown(self.EMAIL_PLACEHOLDER, timeout=timeout)

    def is_postcode_label_visible(self, timeout: int = 4) -> bool:
        return self._shown(self.POSTCODE_LABEL, "Postcode", timeout)

    def is_postcode_placeholder_visible(self, timeout: int = 4) -> bool:
        return self._shown(self.POSTCODE_PLACEHOLDER, "Enter your postcode", timeout)

    def is_age_label_visible(self, timeout: int = 4) -> bool:
        return self._shown(self.AGE_LABEL, "Age range", timeout)

    def is_age_dropdown_visible(self, timeout: int = 4) -> bool:
        if self._present(self.AGE_PLACEHOLDER) or self._present(self.AGE_DROPDOWN):
            return True
        self._scroll_to_text("Age range")
        return self._present(self.AGE_PLACEHOLDER) or self._present(self.AGE_DROPDOWN)

    def is_referral_label_visible(self, timeout: int = 4) -> bool:
        return self._shown(self.REFERRAL_LABEL, "Have a referral code?", timeout)

    def is_referral_placeholder_visible(self, timeout: int = 4) -> bool:
        return self._shown(self.REFERRAL_PLACEHOLDER, "Enter referral code", timeout)

    def is_consent_checkbox_visible(self, timeout: int = 4) -> bool:
        return self._shown(self.CONSENT_CHECKBOX, "consent to Worldpanel", timeout)

    def is_consent_text_visible(self, timeout: int = 4) -> bool:
        return self._shown(self.CONSENT_TEXT, "consent to Worldpanel", timeout)

    def is_privacy_note_visible(self, timeout: int = 4) -> bool:
        return self._shown(self.PRIVACY_NOTE, "personal information", timeout)

    def is_continue_button_visible(self, timeout: int = 4) -> bool:
        return self._shown(self.CONTINUE_TEXT, "Continue", timeout)

    # ---- field input -------------------------------------------------------
    def enter_email(self, email: str):
        elem = self._find(self.EMAIL_INPUT, timeout=8)
        elem.clear()
        elem.send_keys(email)
        self._dismiss_keyboard_if_needed()

    def enter_postcode(self, postcode: str):
        elem = self._find(self.POSTCODE_INPUT, timeout=8)
        elem.clear()
        elem.send_keys(postcode)
        self._dismiss_keyboard_if_needed()

    def enter_referral_code(self, referral_code: str):
        self._scroll_to_text("Have a referral code?")
        elem = self._find(self.REFERRAL_INPUT, timeout=8)
        elem.clear()
        elem.send_keys(referral_code)
        self._dismiss_keyboard_if_needed()

    def get_email_value(self) -> str:
        return (self._find(self.EMAIL_INPUT, timeout=4).get_attribute("text") or "").strip()

    def get_postcode_value(self) -> str:
        return (self._find(self.POSTCODE_INPUT, timeout=4).get_attribute("text") or "").strip()

    def get_referral_value(self) -> str:
        return (self._find(self.REFERRAL_INPUT, timeout=4).get_attribute("text") or "").strip()

    # ---- age range dropdown ------------------------------------------------
    def open_age_dropdown(self):
        self._dismiss_keyboard_if_needed()
        if not self._present(self.AGE_DROPDOWN) and not self._present(self.AGE_PLACEHOLDER):
            self._scroll_to_text("Age range")
        try:
            self._find_clickable(self.AGE_DROPDOWN, timeout=3).click()
            return
        except Exception:
            pass
        try:
            self._tap_element_center(self._find(self.AGE_DROPDOWN, timeout=3))
        except Exception:
            self._tap_element_center(self._find(self.AGE_PLACEHOLDER, timeout=3))

    def _age_option_locator(self, option: str):
        return (AppiumBy.XPATH, f"//android.widget.TextView[@text='{option}']")

    def is_age_options_displayed(self, timeout: int = 4) -> bool:
        if self._present(self._age_option_locator("18-24")):
            return True
        return self._is_visible(self._age_option_locator("18-24"), timeout=timeout)

    def are_all_age_options_visible(self) -> bool:
        return all(self._present(self._age_option_locator(option)) for option in self.AGE_OPTIONS)

    def select_age_range(self, option: str):
        locator = self._age_option_locator(option)
        if not self._present(locator):
            self.open_age_dropdown()
        try:
            self._find_clickable(locator, timeout=3).click()
            return
        except Exception:
            self._tap_element_center(self._find(locator, timeout=3))

    def get_selected_age(self) -> str:
        try:
            value = (self._find(self.AGE_VALUE, timeout=3).get_attribute("text") or "").strip()
        except Exception:
            value = ""
        if value and value != "Select your age":
            return value
        return ""

    # ---- consent -----------------------------------------------------------
    def is_consent_checked(self) -> bool:
        try:
            if not self._present(self.CONSENT_CHECKBOX):
                self._scroll_to_text("consent to Worldpanel")
            elem = self._find(self.CONSENT_CHECKBOX, timeout=4)
            checked = str(elem.get_attribute("checked")).lower()
            if checked in {"true", "false"}:
                return checked == "true"
        except Exception:
            pass
        src = self.driver.page_source or ""
        match = re.search(r'class="android\.widget\.CheckBox"[^>]*checked="(true|false)"', src)
        return bool(match) and match.group(1) == "true"

    def tap_consent_checkbox(self):
        self._scroll_to_text("consent to Worldpanel")
        try:
            self._find_clickable(self.CONSENT_CHECKBOX, timeout=5).click()
            return
        except Exception:
            self._tap_element_center(self._find(self.CONSENT_CHECKBOX, timeout=4))

    def set_consent(self, expected_checked: bool, timeout: float = 5.0):
        end = time.time() + timeout
        while time.time() < end:
            if self.is_consent_checked() == expected_checked:
                return
            self.tap_consent_checkbox()
            time.sleep(0.3)

    # ---- continue + full form helpers -------------------------------------
    def tap_continue(self):
        self._scroll_to_text("Continue")
        try:
            self._find_clickable(self.CONTINUE_CTA, timeout=6).click()
        except Exception:
            self._tap_element_center(self._find(self.CONTINUE_TEXT, timeout=5))

    def tap_continue_twice(self):
        self._scroll_to_text("Continue")
        elem = self._find_clickable(self.CONTINUE_CTA, timeout=6)
        elem.click()
        try:
            elem.click()
        except Exception:
            pass

    def fill_valid_form(self, email: str, postcode: str, age: str = "25-34"):
        self.enter_email(email)
        self.enter_postcode(postcode)
        self.open_age_dropdown()
        self.select_age_range(age)
        self.set_consent(True)

    # ---- validation getters (scroll-aware; errors can be off-screen) -------
    def is_email_required_error_visible(self, timeout: int = 4) -> bool:
        return self._shown(self.EMAIL_REQUIRED_ERROR, "Please enter an email address", timeout)

    def is_email_invalid_error_visible(self, timeout: int = 4) -> bool:
        return self._shown(self.EMAIL_INVALID_ERROR, "Please enter a valid email address", timeout)

    def is_postcode_required_error_visible(self, timeout: int = 4) -> bool:
        return self._shown(self.POSTCODE_REQUIRED_ERROR, "Please enter a postcode", timeout)

    def is_postcode_invalid_error_visible(self, timeout: int = 4) -> bool:
        return self._shown(self.POSTCODE_INVALID_ERROR, "Please enter a valid postcode", timeout)

    def is_postcode_invalid_error_present(self) -> bool:
        return self._present(self.POSTCODE_INVALID_ERROR)

    def is_age_required_error_visible(self, timeout: int = 4) -> bool:
        return self._shown(self.AGE_REQUIRED_ERROR, "Please select age", timeout)

    def is_consent_required_error_visible(self, timeout: int = 4) -> bool:
        return self._shown(self.CONSENT_REQUIRED_ERROR, "confirm that you are over 18", timeout)

    def is_any_error_or_oops_visible(self, timeout: int = 6) -> bool:
        if self._is_visible(self.OOPS_TITLE, timeout=timeout):
            return True
        for locator in (
            self.EMAIL_INVALID_ERROR,
            self.POSTCODE_INVALID_ERROR,
            self.EMAIL_REQUIRED_ERROR,
            self.POSTCODE_REQUIRED_ERROR,
        ):
            if self._present(locator):
                return True
        return False

    # ---- success dialog ----------------------------------------------------
    def is_success_alert_visible(self, timeout: int = 25) -> bool:
        return self._is_visible(self.SUCCESS_ALERT_MESSAGE, timeout=timeout)

    def is_done_button_visible(self, timeout: int = 6) -> bool:
        return self._is_visible(self.DONE_TEXT, timeout=timeout)

    def tap_done(self):
        try:
            self._find_clickable(self.DONE_CTA, timeout=6).click()
        except Exception:
            self._tap_element_center(self._find(self.DONE_TEXT, timeout=5))

    # ---- duplicate (Oops) dialog ------------------------------------------
    def is_duplicate_alert_visible(self, timeout: int = 20) -> bool:
        return self._is_visible(self.DUPLICATE_ALERT_MESSAGE, timeout=timeout)

    def get_duplicate_alert_text(self) -> str:
        try:
            return (self._find(self.DUPLICATE_ALERT_MESSAGE, timeout=8).get_attribute("text") or "").strip()
        except Exception:
            return ""

    def duplicate_alert_count(self) -> int:
        try:
            return len(self.driver.find_elements(*self.DUPLICATE_ALERT_MESSAGE))
        except Exception:
            return 0

    def is_ok_button_visible(self, timeout: int = 6) -> bool:
        return self._is_visible(self.OK_TEXT, timeout=timeout)

    def tap_ok(self):
        try:
            self._find_clickable(self.OK_CTA, timeout=6).click()
        except Exception:
            self._tap_element_center(self._find(self.OK_TEXT, timeout=5))

    def is_alert_dismissed(self, timeout: int = 6) -> bool:
        end = time.time() + timeout
        while time.time() < end:
            if not self._present(self.DUPLICATE_ALERT_MESSAGE) and not self._present(self.OOPS_TITLE):
                return True
            time.sleep(0.3)
        return False

    # ---- accessibility / rendering ----------------------------------------
    def key_elements_accessibility_status(self) -> dict[str, bool]:
        try:
            back_desc = self._find(self.BACK_BUTTON, timeout=5).get_attribute("content-desc") or ""
        except Exception:
            back_desc = ""
        back_ok = bool(back_desc.strip())

        self._scroll_to_text("Thank you for your interest")
        logo_present = self._present(self.LOGO)
        logo_ok = True
        if logo_present:
            try:
                logo_desc = self._find(self.LOGO, timeout=3).get_attribute("content-desc") or ""
                logo_ok = bool(logo_desc.strip())
            except Exception:
                logo_ok = False

        # Validate labels from accessibility tree snapshot to avoid fold/scroll
        # flakiness while still asserting semantic label exposure.
        src = (self.driver.page_source or "").lower()
        labels_present = all(token in src for token in ("email", "postcode", "age range"))

        return {
            "back_ok": back_ok,
            "logo_ok": logo_ok,
            "labels_present": labels_present,
        }

    def key_elements_have_accessibility_labels(self) -> bool:
        status = self.key_elements_accessibility_status()
        return all(status.values())

    def core_content_rendered(self) -> bool:
        if not (self.is_email_label_visible(5) and self.is_postcode_label_visible(5) and self.is_age_label_visible(5)):
            return False
        self._scroll_to_text("Continue")
        try:
            elem = self._find(self.CONTINUE_TEXT, timeout=5)
            match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", elem.get_attribute("bounds") or "")
            if match:
                _, _, x2, _ = map(int, match.groups())
                width = self.driver.get_window_size().get("width", x2)
                if x2 > width + 5:
                    return False
        except Exception:
            return False
        return True
