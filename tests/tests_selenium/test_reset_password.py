import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tests.tests_selenium.conftest import register_user, login_user

def test_reset_password_flow(live_server, browser):
    user_username = "reset_password_user"
    user_email = "reset_password_user@example.com"
    user_password = "Secret123!"

    register_user(browser, live_server, user_username, user_email, user_password)

    browser.get(f"{live_server}/auth/reset_password_request")
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.NAME, "email")))
    browser.find_element(By.NAME, "email").send_keys(user_email)
    browser.find_element(By.CSS_SELECTOR, "input[type=submit],button[type=submit]").click()
    WebDriverWait(browser, 10).until(EC.url_contains("/auth/login"))
    assert "Check your email for the instructions to reset your password" in browser.page_source