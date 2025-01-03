import os
from appium.webdriver.common.appiumby import AppiumBy
from pageobjects.basepage import BasePage, WaitCondition
from pageobjects.basepage import BasePage
from pageobjects.bc_wallet.enable_notifications import EnableNotificationsPage

class OnboardingBiometricsPage(BasePage):
    """Onboarding Biometrics page object"""

    # Locators
    on_this_page_text_locator = "Use biometrics to unlock wallet"
    on_this_page_locator = (AppiumBy.ID, "com.ariesbifold:id/ToggleBiometrics")
    use_biometrics_toggle_locator = (AppiumBy.ID, "com.ariesbifold:id/ToggleBiometrics")
    continue_button_locator = (AppiumBy.ID, "com.ariesbifold:id/Continue")

    def __init__(self, driver):
        super().__init__(driver)
        # Instantiate possible Modals and Alerts for this page
        self.enable_biometrics_system_modal = EnableBiometricsSystemModal(driver)

    def on_this_page(self):   
        timeout = 50
        if "Local" in os.environ['DEVICE_CLOUD']:
            timeout = 100
        return super().on_this_page(self.on_this_page_locator, timeout)  

    # this no longer exists in build 305 but leaving it in as it is uncertain if it will come back.
    def select_biometrics(self):
        if self.on_this_page():
            self.find_by(self.use_biometrics_toggle_locator).click()
            return True
        else:
            raise Exception(f"App not on the {type(self)} page")


    def select_continue(self):
        if self.on_this_page():
            self.find_by(self.continue_button_locator).click()

            # return the wallet enable notifications page
            return EnableNotificationsPage(self.driver)
            
        else:
            raise Exception(f"App not on the {type(self)} page")


class EnableBiometricsSystemModal(BasePage):
    """Enable Biometrics System Modal page object"""

    # Locators
    on_this_page_text_locator = "BC Wallet wants to use your"
    on_this_page_locator = (AppiumBy.ID, "com.ariesbifold:id/Allow")
    allow_button_locator = (AppiumBy.ID, "com.ariesbifold:id/Allow")
    dont_allow_button_locator = (AppiumBy.ID, "com.ariesbifold:id/DontAllow")

    def on_this_page(self):    
        return super().on_this_page(self.on_this_page_locator) 

    def select_allow(self):
        self.find_by(self.allow_button_locator, wait_condition=WaitCondition.PRESENCE_OF_ELEMENT_LOCATED).click()
        return OnboardingBiometricsPage(self.driver)
    
        # if self.driver.capabilities['platformName'] == 'Android':
        #     self.select_system_allow_while_using_app()
        # return True

    def select_dont_allow(self):
        self.find_by(self.dont_allow_button_locator, wait_condition=WaitCondition.PRESENCE_OF_ELEMENT_LOCATED).click()
        return OnboardingBiometricsPage(self.driver)