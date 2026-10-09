from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class HomePage:
    HOME_HEADER = (AppiumBy.ID, "com.kantarworldpanel.shoppix:id/img_header")
    MENU_SETTINGS = (AppiumBy.ID, "com.kantarworldpanel.shoppix:id/menu_action_setting")
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

    def logout_from_menu(self):
        self._find_clickable(self.MENU_SETTINGS, timeout=20).click()

        self._scroll_to_sign_out()
        self._find_clickable(self.SIGN_OUT_ROW, timeout=12).click()

        self._find(self.SIGN_OUT_CONFIRM_TEXT, timeout=12)
        self._find_clickable(self.SIGN_OUT_YES, timeout=8).click()
