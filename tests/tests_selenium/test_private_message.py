from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def register_user(browser, live_server, username, email, password):
    """Helper function to register a new user"""
    browser.get(f"{live_server}/auth/register")
    
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    browser.find_element(By.NAME, "username").clear()
    browser.find_element(By.NAME, "username").send_keys(username)
    browser.find_element(By.NAME, "email").clear()
    browser.find_element(By.NAME, "email").send_keys(email)
    browser.find_element(By.NAME, "password").clear()
    browser.find_element(By.NAME, "password").send_keys(password)
    browser.find_element(By.NAME, "password2").clear()
    browser.find_element(By.NAME, "password2").send_keys(password)
    
    browser.find_element(By.CSS_SELECTOR, "input[type=submit],button[type=submit]").click()
    WebDriverWait(browser, 10).until(
        EC.url_contains("/auth/login")
    )


def login_user(browser, live_server, username, password):
    """Helper function to log in a user"""
    browser.get(f"{live_server}/auth/login")
    
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    browser.find_element(By.NAME, "username").clear()
    browser.find_element(By.NAME, "username").send_keys(username)
    browser.find_element(By.NAME, "password").clear()
    browser.find_element(By.NAME, "password").send_keys(password)
    
    browser.find_element(By.CSS_SELECTOR, "input[type=submit],button[type=submit]").click()
    WebDriverWait(browser, 10).until(
        lambda d: "/auth/login" not in d.current_url
    )


def logout_user(browser):
    """Helper function to log out current user"""
    browser.find_element(By.LINK_TEXT, "Logout").click()
    WebDriverWait(browser, 10).until(
        EC.url_contains("/auth/login")
    )


def test_private_message_flow(live_server, browser):
    # Test data
    user1_username = "message_user1"
    user1_email = "message_user1@example.com"
    user1_password = "Secret123!"
    
    user2_username = "message_user2"
    user2_email = "message_user2@example.com"
    user2_password = "Secret123!"
    
    message_text = "Hello! This is a test private message."
    
    # Register both users
    register_user(browser, live_server, user1_username, user1_email, user1_password)
    register_user(browser, live_server, user2_username, user2_email, user2_password)
    
    # Log in as user 1
    login_user(browser, live_server, user1_username, user1_password)
    
    # Navigate to user 2's profile and send a private message
    browser.get(f"{live_server}/user/{user2_username}")
    
    # Find send private message, fill out the form, check if message was sent
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.LINK_TEXT, "Send private message"))
    )
    browser.find_element(By.LINK_TEXT, "Send private message").click()

    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.NAME, "message"))
    )

    browser.find_element(By.NAME, "message").send_keys(message_text)
    browser.find_element(By.CSS_SELECTOR, "input[type=submit],button[type=submit]").click()

    WebDriverWait(browser, 10).until(
        EC.url_contains(f"/user/{user2_username}")
    )

    page_source = browser.page_source
    assert "Your message has been sent." in page_source
    
    # Log out user 1
    logout_user(browser)
    
    # Log in user 2
    login_user(browser, live_server, user2_username, user2_password)
    
    # Navigate to messages page and check for the received message
    browser.get(f"{live_server}/messages")

    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    page_source = browser.page_source
    assert message_text in page_source
    assert user1_username in page_source  # Should show sender username
