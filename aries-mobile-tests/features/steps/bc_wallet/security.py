# -----------------------------------------------------------
# Behave Step Definitions for Terms and Conditions rejection or acceptance.
# 
# -----------------------------------------------------------

from behave import given, when, then, step
import json
import os
from decouple import config
from time import sleep

# Local Imports
from agent_controller_client import agent_controller_GET, agent_controller_POST, expected_agent_state, setup_already_connected
from agent_test_utils import get_qr_code_from_invitation
# import Page Objects needed
from pageobjects.bc_wallet.termsandconditions import TermsAndConditionsPage
from pageobjects.bc_wallet.secure import SecurePage
from pageobjects.bc_wallet.home import HomePage
from pageobjects.bc_wallet.navbar import NavBar
from pageobjects.bc_wallet.pinsetup import PINSetupPage
from pageobjects.bc_wallet.biometrics import BiometricsPage
from pageobjects.bc_wallet.pin import PINPage


@given('the User has accepted the Terms and Conditions')
def step_impl(context):
    context.execute_steps(f'''
        Given the User is on the Terms and Conditions screen
        And the users accepts the Terms and Conditions
    ''')


@when('the User enters the first PIN as {pin}')
@when('the User enters the first PIN as "{pin}"')
def step_impl(context, pin):
    context.thisPINSetupPage.enter_pin(pin)
    # TODO remove comment here when Test IDs are on the visibility toggle
    #assert pin == context.thisPINSetupPage.get_pin()


@when('the User re-enters the PIN as {pin}')
@then('the User re-enters the PIN as {pin}')
@then('the User re-enters the PIN as "{pin}"')
@when('the User re-enters the PIN as "{pin}"')
def step_impl(context, pin):
    context.thisPINSetupPage.enter_second_pin(pin)
    # TODO remove comment here when Test IDs are on the visibility toggle
    #assert pin == context.thisPINSetupPage.get_second_pin()


@then('the User selects Create PIN')
@when('the User selects Create PIN')
def step_impl(context):
    context.thisOnboardingBiometricsPage = context.thisPINSetupPage.create_pin()


@step('the User allows notifications')
def step_enable_notifications(context):
    assert context.thisEnableNotificationsPage.on_this_page()
    context.thisInitializationPage = context.thisEnableNotificationsPage.select_continue()
    #context.thisOnboardingBiometricsPage = context.thisEnableNotificationsPage.select_continue()
    # Capabilities are setup to automatically accept system alerts.
    #context.thisEnableNotificationsSystemModal = context.thisEnableNotificationsPage.select_continue()
    #assert context.thisEnableNotificationsSystemModal.on_this_page()
    #context.thisOnboardingBiometricsPage = context.thisEnableNotificationsSystemModal.select_allow()

@step('the User does not allow notifications')
def step_enable_notifications(context):
    assert context.thisEnableNotificationsPage.on_this_page()
    context.thisEnableNotificationsSystemModal = context.thisEnableNotificationsPage.select_continue()
    assert context.thisEnableNotificationsSystemModal.on_this_page()
    context.thisInitializationPage = context.thisEnableNotificationsSystemModal.select_dont_allow()

@when('the User selects to use Biometrics')
def step_impl(context):
    assert context.thisOnboardingBiometricsPage.on_this_page()
    assert context.thisOnboardingBiometricsPage.select_biometrics()
    
    # Build 2084+ now has a system modal that needs to be accepted.
    #assert context.thisOnboardingBiometricsPage.enable_biometrics_system_modal.on_this_page()
    #context.thisOnboardingBiometricsPage.enable_biometrics_system_modal.select_allow()
    # Until SauceLabs Case #00155429 is resolved, we need to authenticate with biomtrics. 
    # 2 Lined above are commented out in the meantime,
    context.device_service_handler.biometrics_authenticate(True)
    
    context.thisEnableNotificationsPage = context.thisOnboardingBiometricsPage.select_continue()

    # This is causing the test to fail when using a local android device so make this line conditional
    if "Local" not in os.environ['DEVICE_CLOUD']:
        context.device_service_handler.biometrics_authenticate(True)

@then('they have access to the app')
def step_impl(context):
    # The Home page will not show until the initialization page is done. 
    #assert context.thisInitializationPage.on_this_page()
    #context.thisHomePage = context.thisInitializationPage.wait_until_initialized()
    if context.thisHomePage.welcome_to_bc_wallet_modal.is_displayed():
        context.thisHomePage.welcome_to_bc_wallet_modal.select_dismiss()
        assert True
    else:
        assert context.thisHomePage.on_this_page()

@then('they land on the Home screen')
@when('initialization ends (failing silently)')
def step_impl(context):
    # The Home page will not show until the initialization page is done. 
    #assert context.thisInitializationPage.on_this_page()
    context.thisHomePage = context.thisInitializationPage.wait_until_initialized()
    context.thisNavBar = NavBar(context.driver)
    if context.thisHomePage.welcome_to_bc_wallet_modal.is_displayed():
        context.thisHomePage.welcome_to_bc_wallet_modal.select_dismiss()
    assert context.thisHomePage.on_this_page()

    # set the environment to TEST instead of PROD which is default as of build 575
    # check to see what the current environment is set to. Order of presendence is, Environment Variable, Tag, default. 
    env = os.environ.get('BCWALLET_ENVIRONMENT')
    
    if not env:
        for tag in context.tags:
            if tag.startswith('@BCWALLET_ENVIRONMENT:'):
                env = tag.split(':')[1]

    if env:
        context.execute_steps(f'''
            Given the App environment is set to {env}
        ''')


@given('the App environment is set to {env}')
def step_impl(context, env):
    context.thisSettingsPage = context.thisHomePage.select_settings()
    context.thisSettingsPage.enable_developer_mode()
    context.thisDeveloperSettingsPage = context.thisSettingsPage.select_developer()
    context.thisDeveloperSettingsPage.select_env(env)
    context.thisSettingsPage = context.thisDeveloperSettingsPage.select_back()
    context.thisSettingsPage.select_back()
    if context.thisHomePage.welcome_to_bc_wallet_modal.is_displayed():
        context.thisHomePage.welcome_to_bc_wallet_modal.select_dismiss()
    assert context.thisHomePage.on_this_page()


@given('the Holder has setup biometrics on thier device')
def step_impl(context):
    # Assume already setup. TODO May need to actually do the setup here eventually.
    pass

@given('the Holder has selected to use biometrics to unlock BC Wallet')
def step_impl(context):
    context.biometrics_choosen = True
    context.execute_steps('''
        When the User selects to use Biometrics
        And the User allows notifications
        Then they land on the Home screen
    ''')
    

@when('they have closed the app')
@given('they have closed the app')
def step_impl(context):
    context.driver.terminate_app(context.driver.capabilities[get_package_or_bundle_id(context)])

@when('the holder opens BC Wallet')
@when('they relaunch the app')
def step_impl(context):
    context.driver.activate_app(context.driver.capabilities[get_package_or_bundle_id(context)])
    # There is a crash issue in the automation when entering the pin right after a restart.
    # wait 5 seconds to stop the crashing or minimize at least.
    sleep(5)

def get_package_or_bundle_id(context):
    if context.driver.capabilities['platformName'] == 'iOS':
        package_or_bundle_id = 'bundleId'
    else:
        package_or_bundle_id = 'appPackage'
    return package_or_bundle_id

@when('authenticates with thier biometrics')
def step_impl(context):
    # Check to see if the Biometrics page is displayed
    #if ('autoGrantPermissions' in context.driver.capabilities and context.driver.capabilities['autoGrantPermissions'] == False) or (context.driver.capabilities['platformName'] == 'iOS'):
    if (context.driver.capabilities['platformName'] == 'iOS'):
        context.thisBiometricsPage = BiometricsPage(context.driver)
        assert context.thisBiometricsPage.on_this_page()
        context.device_service_handler.biometrics_authenticate(True)
        assert context.thisBiometricsPage.on_this_page() == False
        # Check to make sure we are not already on the home page.
        if context.thisHomePage.on_this_page() == False:
            context.thisInitializationPage.wait_until_initialized()


@when('fails to authenticate with thier biometrics once')
def step_impl(context):
    if hasattr(context, 'thisBiometricsPage') == False:
        context.thisBiometricsPage = BiometricsPage(context.driver)

    assert context.thisBiometricsPage.on_this_page()
    context.device_service_handler.biometrics_authenticate(False)
    #assert context.thisBiometricsPage.on_this_page()


@step('the User continues from reviewing Secure your Wallet')
def step_impl(context):
    assert context.thisWhyYouNeedAPINPage.on_this_page()
    context.thisPINSetupPage = context.thisWhyYouNeedAPINPage.select_continue()

@when('they enter thier PIN as "{pin}"')
def step_impl(context, pin):
    if hasattr(context, 'thisPINPage') == False:
        context.thisPINPage = PINPage(context.driver)

    context.thisPINPage.enter_pin(pin)

    context.thisInitializationPage = context.thisPINPage.select_enter()


@then('they are informed that the PINs do not match')
def step_impl(context):
    context.thisPINSetupPage.does_pin_match()


@then('they select ok on PINs do not match')
def step_impl(context):
    context.thisPINSetupPage.select_ok_on_modal()


@then('they are informed of {pin_error}')
def step_impl(context, pin_error):
    assert context.thisPINSetupPage.get_pin_error() == pin_error



@given('the user has choosen to have biometrics {bio_usage}')
def step_biometrics_choosen(context, bio_usage:str):
    if bio_usage == 'on':
        context.execute_steps('''
            Given the Holder has selected to use biometrics to unlock BC Wallet
        ''')
    else:
        context.execute_steps('''
            Given the User has choosen not to use biometrics to unlock BC Wallet
        ''')

@when('the user updates thier PIN to "{pin}"')
def step_update_pin(context, pin):
    context.execute_steps(f'''
        Given the user wants to update thier PIN
        When the user enters thier old PIN as "369369"
        And the user enters thier first PIN as "{pin}"
        And the User re-enters the PIN as "{pin}"
        And the User selects Change PIN
        And the User has successfully updated PIN
    ''')


@then('they have access to the app with the new PIN')
def step_access_app_with_pin(context):
    assert context.thisSettingsPage.on_this_page()
    context.thisHomePage = context.thisSettingsPage.select_back()
    assert context.thisHomePage.on_this_page()

    context.execute_steps('''
        Given they have closed the app
        When they relaunch the app
    ''')
    
    context.thisBiometricsPage = BiometricsPage(context.driver)
    if context.thisBiometricsPage.on_this_page():
        context.execute_steps('''
            When fails to authenticate with thier biometrics once
        ''')                

    context.execute_steps('''
        When they enter thier PIN as "963963"
        Then they have access to the app
    ''')

@given('the User has choosen not to use biometrics to unlock BC Wallet')
def step_impl(context):
    context.biometrics_choosen = False
    context.thisEnableNotificationsPage = context.thisOnboardingBiometricsPage.select_continue()
    context.execute_steps('''
        Given the User allows notifications
        Then they land on the Home screen
    ''')

@given('the user wants to update thier PIN')
def go_to_pin_update(context):
    context.thisSettingsPage = context.thisHomePage.select_settings()
    context.thisChangePINPage = context.thisSettingsPage.select_change_pin()

@when('the user enters thier old PIN as "{pin}"')
def step_enter_old_pin(context, pin):
    context.thisChangePINPage.enter_old_pin(pin)

@when('the user enters thier first PIN as "{pin}"')
def step_enter_first_pin(context, pin):
    context.thisChangePINPage.enter_pin(pin)

@when('the user re-enters thier PIN as "{pin}"')
@then('the user re-enters thier PIN as "{pin}"')
def step_reenter_first_pin(context, pin):
    context.thisChangePINPage.reenter_pin(pin)

@when('the User selects Change PIN')
@then('the User selects Change PIN')
def step_select_change_pin(context):
    context.thisChangePINPage.select_change_pin()

@when('the User has successfully updated PIN')
@then('the User has successfully updated PIN')
def step_select_update_pin(context):
    assert context.thisChangePINPage.successfully_changed_pin_modal.is_displayed()
    context.thisSettingsPage = context.thisChangePINPage.successfully_changed_pin_modal.select_okay()

