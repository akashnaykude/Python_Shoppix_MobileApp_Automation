from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class HomePage:
    HOME_HEADER = (AppiumBy.ID, "com.kantarworldpanel.shoppix:id/img_header")
    MENU_SETTINGS = (AppiumBy.ID, "com.kantarworldpanel.shoppix:id/menu_action_setting")
    TUTORIAL_SKIP = (AppiumBy.XPATH, "//android.widget.TextView[@text='Skip']")
    TUTORIAL_TITLE = (AppiumBy.XPATH, "//android.widget.TextView[@text='We are Shoppix!']")
    LOADING_MESSAGE = (AppiumBy.ID, "com.kantarworldpanel.shoppix:id/dialog_message")
    SETTINGS_ROW = (
        AppiumBy.XPATH,
        "//android.widget.TextView[@text='Settings']/ancestor::android.view.View[@clickable='true'][1]",
    )
    DELETE_ACCOUNT_ROW = (
        AppiumBy.XPATH,
        "//android.widget.TextView[contains(translate(@text,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'delete') and contains(translate(@text,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'account')]/ancestor::android.view.View[@clickable='true'][1]",
    )
    DELETE_ACCOUNT_PASSWORD_INPUT = (
        AppiumBy.XPATH,
        "//android.widget.EditText",
    )
    DELETE_MY_ACCOUNT_CTA = (
        AppiumBy.XPATH,
        "//android.widget.TextView[contains(translate(@text,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'delete my account')]/ancestor::android.view.View[@clickable='true'][1]",
    )
    DELETE_CONFIRM_CTA = (
        AppiumBy.XPATH,
        "//android.widget.TextView[@text='Delete']/ancestor::android.view.View[@clickable='true'][1]",
    )
    DELETE_PASSWORD_CONTINUE_CTA = (
        AppiumBy.XPATH,
        "//android.widget.TextView[@text='Continue']/ancestor::android.view.View[@clickable='true'][1]",
    )
    OOPS_TITLE = (AppiumBy.XPATH, "//android.widget.TextView[@text='Oops']")
    OOPS_OK = (AppiumBy.XPATH, "//android.widget.TextView[@text='OK']")
    TOO_MANY_REQUESTS = (
        AppiumBy.XPATH,
        "//android.widget.TextView[contains(@text,'Too many requests') and contains(@text,'Please try again later')]",
    )
    SIGN_OUT_ROW = (
        AppiumBy.XPATH,
        "//android.widget.TextView[@text='Sign Out']/ancestor::android.view.View[@clickable='true'][1]",
    )
    SIGN_OUT_CONFIRM_TEXT = (
        AppiumBy.XPATH,
        "//android.widget.TextView[@text='Are you sure you wish to sign out?']",
    )
    SIGN_OUT_YES = (AppiumBy.XPATH, "//android.widget.TextView[@text='Yes']")

    def __init__(self, driver):
        self.driver = driver

    def _find(self, locator, timeout: int = 20):
        return WebDriverWait(self.driver, timeout).until(ec.presence_of_element_located(locator))

    def _find_clickable(self, locator, timeout: int = 20):
        return WebDriverWait(self.driver, timeout).until(ec.element_to_be_clickable(locator))

    def _is_visible(self, locator, timeout: int = 3) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(ec.visibility_of_element_located(locator))
            return True
        except Exception:
            return False

    def _present(self, locator) -> bool:
        # Non-blocking presence check (no implicit wait is configured).
        try:
            return len(self.driver.find_elements(*locator)) > 0
        except Exception:
            return False

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
                f'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView(new UiSelector().textContains("{text}"));',
            )
        except Exception:
            pass

    def _scroll_to_sign_out(self, max_swipes: int = 8):
        if self._is_visible(self.SIGN_OUT_ROW, timeout=2):
            return

        rect = self.driver.get_window_rect()
        left = int(rect["x"] + rect["width"] * 0.08)
        top = int(rect["y"] + rect["height"] * 0.25)
        width = int(rect["width"] * 0.84)
        height = int(rect["height"] * 0.55)

        for _ in range(max_swipes):
            self.driver.execute_script(
                "mobile: scrollGesture",
                {
                    "left": left,
                    "top": top,
                    "width": width,
                    "height": height,
                    "direction": "down",
                    "percent": 0.85,
                },
            )
            if self._is_visible(self.SIGN_OUT_ROW, timeout=2):
                return

        # Fallback for devices where gesture scroll doesn't move the expected container.
        self.driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView(new UiSelector().text("Sign Out"));',
        )

    def is_home_header_visible(self, timeout: int = 20) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(ec.visibility_of_element_located(self.HOME_HEADER))
            return True
        except Exception:
            return False

    def is_tutorial_visible(self, timeout: int = 2) -> bool:
        return self._present(self.TUTORIAL_SKIP) or self._present(self.TUTORIAL_TITLE)

    def is_loading_visible(self, timeout: int = 2) -> bool:
        if self._is_visible(self.LOADING_MESSAGE, timeout=timeout):
            return True
        src = (self.driver.page_source or "").lower()
        return "loading..." in src

    def is_too_many_requests_visible(self, timeout: int = 2) -> bool:
        if not self._present(self.OOPS_TITLE):
            return False
        if self._present(self.TOO_MANY_REQUESTS):
            return True
        src = (self.driver.page_source or "").lower()
        return "too many requests" in src and "please try again later" in src

    def is_home_like_state(self) -> bool:
        src = (self.driver.page_source or "").lower()
        if "menu_action_setting" in src or "img_header" in src:
            return True
        if "my profile" in src and "settings" in src and "rewards" in src:
            return True
        if "navigate to settings" in src and "privacy policy" in src:
            return True
        return False

    def dismiss_oops_if_present(self, timeout: int = 2) -> bool:
        if not self._is_visible(self.OOPS_TITLE, timeout=timeout):
            return False
        try:
            self._find_clickable(self.OOPS_OK, timeout=3).click()
            return True
        except Exception:
            return False

    def wait_for_post_registration_state(self, timeout: int = 35) -> str:
        # Use polling loop because destination can move: loading -> tutorial -> home.
        import time

        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.is_too_many_requests_visible():
                return "rate_limited"
            if self._present(self.HOME_HEADER) or self.is_home_like_state():
                return "home"
            if self.is_tutorial_visible():
                return "tutorial"
            time.sleep(0.5)
        return "unknown"

    def skip_tutorial_if_present(self, timeout: int = 25) -> bool:
        import time

        if not self.is_tutorial_visible():
            return self.is_home_header_visible(timeout=4)

        self._find_clickable(self.TUTORIAL_SKIP, timeout=6).click()
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self._present(self.HOME_HEADER):
                return True
            time.sleep(0.5)
        return False

    def open_settings_from_home(self):
        if not self._present(self.SETTINGS_ROW):
            self._find_clickable(self.MENU_SETTINGS, timeout=20).click()
        self._find_clickable(self.SETTINGS_ROW, timeout=12).click()

    def delete_account_from_settings(self, password: str) -> bool:
        import time

        self._scroll_to_text("Delete")
        try:
            self._find_clickable(self.DELETE_ACCOUNT_ROW, timeout=8).click()
        except Exception:
            return False

        # Flow (screen order can vary): info screen -> "Delete my account" ->
        # password screen -> enter password -> "Continue" -> "Are you sure" dialog ->
        # "Delete" -> welcome/login. Drive it as a state loop so any order works.
        password_entered = False
        deadline = time.time() + 45
        while time.time() < deadline:
            src = (self.driver.page_source or "").lower()

            if any(marker in src for marker in ("get started", "login as existing user", "welcome back")):
                return True

            # Final confirmation dialog.
            if "are you sure" in src and self._present(self.DELETE_CONFIRM_CTA):
                try:
                    self._find_clickable(self.DELETE_CONFIRM_CTA, timeout=3).click()
                    continue
                except Exception:
                    pass

            # Password screen: type password, then Continue (enables once filled).
            if self._present(self.DELETE_ACCOUNT_PASSWORD_INPUT):
                if not password_entered:
                    self._dismiss_keyboard_if_needed()
                    try:
                        field = self._find(self.DELETE_ACCOUNT_PASSWORD_INPUT, timeout=3)
                        field.clear()
                        field.send_keys(password)
                        password_entered = True
                    except Exception:
                        pass
                    self._dismiss_keyboard_if_needed()
                try:
                    self._find_clickable(self.DELETE_PASSWORD_CONTINUE_CTA, timeout=4).click()
                    continue
                except Exception:
                    pass

            # Info/warning screen: proceed with "Delete my account".
            if self._present(self.DELETE_MY_ACCOUNT_CTA):
                try:
                    self._find_clickable(self.DELETE_MY_ACCOUNT_CTA, timeout=3).click()
                    continue
                except Exception:
                    pass

            time.sleep(0.4)

        return False

    def cleanup_newly_registered_account(self, password: str) -> bool:
        if self.is_tutorial_visible(timeout=2):
            if not self.skip_tutorial_if_present(timeout=25):
                return False

        if not self.is_home_header_visible(timeout=10):
            return False

        self.open_settings_from_home()
        return self.delete_account_from_settings(password)

    def logout_from_menu(self):
        self._find_clickable(self.MENU_SETTINGS, timeout=20).click()

        self._scroll_to_sign_out()
        self._find_clickable(self.SIGN_OUT_ROW, timeout=12).click()

        self._find(self.SIGN_OUT_CONFIRM_TEXT, timeout=12)
        self._find_clickable(self.SIGN_OUT_YES, timeout=8).click()
