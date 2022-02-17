# -----------------------------------------------------------
# Behave environtment file used to hold test hooks to do
# Setup and Tear Downs at different levels
# For more info see:
# https://behave.readthedocs.io/en/latest/tutorial.html#environmental-controls
#  
# -----------------------------------------------------------
from appium import webdriver
import allure
from sauceclient import SauceClient
from decouple import config
import os, json
import hmac
from hashlib import md5

config_file_path = os.path.join(os.path.dirname(__file__), '..', "config.json")
print("Path to the config file = %s" % (config_file_path))
with open(config_file_path) as config_file:
    CONFIG = json.load(config_file)

# Take user credentials from environment variables if they are defined
#if 'BROWSERSTACK_USERNAME' in os.environ: CONFIG['capabilities']['browserstack.user'] = os.environ['BROWSERSTACK_USERNAME'] 
#if 'BROWSERSTACK_ACCESS_KEY' in os.environ: CONFIG['capabilities']['browserstack.key'] = os.environ['BROWSERSTACK_ACCESS_KEY']

# Take user credentials and sauce region from environment variables if they are defined
# TODO this should be in a separate module that handles device service specific variable settings.
username = config('SAUCE_USERNAME')
access_key = config('SAUCE_ACCESS_KEY')
#if 'SAUCE_USERNAME' in os.environ: username = os.environ['SAUCE_USERNAME'] 
#if 'SAUCE_ACCESS_KEY' in os.environ: access_key = os.environ['SAUCE_ACCESS_KEY']
#url = 'http://%s:%s@ondemand.saucelabs.com:80/wd/hub' % (username, access_key)
region = config('SL_REGION')
url = 'http://%s:%s@ondemand.%s.saucelabs.com:80/wd/hub' % (username, access_key, region)
print(url)

def before_feature(context, feature):
    #CONFIG['capabilities']['sauce:options']['name'] = feature.name
    CONFIG['capabilities']['name'] = feature.name
    desired_capabilities = CONFIG['capabilities']
    print(desired_capabilities)
    # context.driver = webdriver.Remote(
    #     desired_capabilities=desired_capabilities,
    #     command_executor="http://hub-cloud.browserstack.com/wd/hub"
    # )
    context.driver = webdriver.Remote(
        desired_capabilities=desired_capabilities,
        command_executor=url,
        keep_alive=True
    )
    print(json.dumps(context.driver.capabilities))
    #context.driver = webdriver.Remote(url, desired_capabilities)

    # Set the Issuer and Verfier URLs
    context.issuer_url = context.config.userdata.get("Issuer")
    context.verifier_url = context.config.userdata.get("Verifier")

def after_scenario(context, scenario):

    device_cloud_service = os.environ['DEVICE_CLOUD']
    if device_cloud_service == "SauceLabs":

        # Add the sauce Labs results and video url to the allure results
        # Link that requires a sauce labs account and login
        testobject_test_report_url = context.driver.capabilities["testobject_test_report_url"]
        allure.attach(testobject_test_report_url, "Sauce Labs Report and Video (Login required)")
        print(f"Sauce Labs Report and Video (Login required): {testobject_test_report_url}")

        # Link does not require a sauce labs account and login. Token generated.
        # TODO This isn't working. Have contacted Sauce Labs. 
        test_id = testobject_test_report_url.rpartition('/')[-1]
        session_id = context.driver.session_id
        key = f"{username}:{access_key}"
        sl_token = hmac.new(key.encode("ascii"), None, md5).hexdigest()
        url = f"{testobject_test_report_url}?auth={sl_token}"
        allure.attach(url, "Public Sauce Labs Report and Video (Login not required) (Nonfunctional at this time)")
        print(f"Public Sauce Labs Report and Video (Login not required): {url} (Nonfunctional at this time)")

    # elif device_cloud_service == "something else in the future":

def after_feature(context, feature):
    # Invoke driver.quit() after the test is done to indicate to BrowserStack 
    # that the test is completed. Otherwise, test will appear as timed out on BrowserStack.
    # if context does not contain browser then something went wrong on initialization and no need to call quit.
    if hasattr(context, 'driver'):
        context.driver.quit()


