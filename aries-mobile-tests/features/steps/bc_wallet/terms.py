# -----------------------------------------------------------
# Behave Step Definitions for Terms and Conditions rejection or acceptance.
# 
# -----------------------------------------------------------

from behave import given, when, then
import json

# Local Imports
from agent_controller_client import agent_controller_GET, agent_controller_POST, expected_agent_state, setup_already_connected
from agent_test_utils import get_qr_code_from_invitation
# import Page Objects needed
from pageobjects.bc_wallet.termsandconditions import TermsAndConditionsPage
from pageobjects.bc_wallet.secure import SecurePage
from pageobjects.bc_wallet.onboardingwelcome import OnboardingWelcomePage
from pageobjects.bc_wallet.onboardingtakecontrol import OnboardingTakeControlPage


@given('the User has completed on-boarding')
def step_impl(context):
    context.execute_steps(f'''
            Given the new user has opened the app for the first time
            Given the user is on the onboarding Welcome screen
            When the user selects Next
            And they are brought to the Store your credentials securely screen
            And the user selects Next
            And they are brought to the Share only what is neccessary screen
            And the user selects Next
            And they are brought to the Take control of your information screen
            Then they can select Get started
        ''')

@given('the User is on the Terms and Conditions screen')
def step_impl(context):
    context.execute_steps(f'''
            Then are brought to the Terms and Conditions screen
        ''')


@when('the User scrolls to the bottom of the screen')
def step_impl(context):
    assert context.thisTermsAndConditionsPage.scroll_to_element(context.thisTermsAndConditionsPage.back_locator, 1500)


@when('the users accepts the Terms and Conditions')
def step_impl(context):
    context.thisTermsAndConditionsPage.select_accept()


@when('the user clicks continue')
def step_impl(context):
    context.thisSecurePage = context.thisTermsAndConditionsPage.select_continue()


@then('the user transitions to the PIN creation screen')
def step_impl(context):
    context.thisSecurePage.on_this_page()


@when('the User presses the back button')
def step_impl(context):
    context.thisCurrentOnboardingPage = context.thisTermsAndConditionsPage.select_back()
    #context.thisOnboardingWelcomePage = OnboardingWelcomePage(context.thisTermsAndConditionsPage.select_back())


# TODO change this to any of the onboarding pages. iOS Bug Issue Number: 
@then('the User goes back to the last on-boarding screen they viewed')
def step_impl(context):
    assert context.thisOnboardingTakeControlPage.on_this_page()
    