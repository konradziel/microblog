import time


from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from tests.tests_selenium.conftest import register_user, login_user

def test_follow_unfollow_functionality(live_server, browser):
    wait = WebDriverWait(browser, timeout=2)
    user1_username = "follow_user1"
    user1_email = "follow_user1@example.com"
    user1_password = "Secret123!"

    user2_username = "follow_user2"
    user2_email = "follow_user2@example.com"
    user2_password = "Secret123!"

    register_user(browser, live_server, user1_username, user1_email, user1_password)
    register_user(browser, live_server, user2_username, user2_email, user2_password)

    login_user(browser, live_server, user1_username, user1_password)

    browser.get(f"{live_server}/user/{user2_username}")

    time.sleep(2)

    user_follows = browser.find_element(By.XPATH, "//p[contains(text(), 'followers')]")
    assert '0 followers' in user_follows.text, f"Expected '0 followers', but got: {user_follows.text}"
    assert '0 following' in user_follows.text, f"Expected '0 following', but got: {user_follows.text}"

    follow_button = browser.find_element(By.XPATH, "//input[@type='submit' and @value='Follow']")
    follow_button.click()

    wait.until(lambda d: d.current_url == f"{live_server}/user/{user2_username}")
    time.sleep(2)

    unfollow_button = browser.find_element(By.XPATH, "//input[@type='submit' and @value='Unfollow']")
    assert unfollow_button.is_displayed(), "Unfollow button should be visible after following."

    user_follows = browser.find_element(By.XPATH, "//p[contains(text(), 'followers')]")
    assert '1 follower' in user_follows.text, \
        f"Expected '1 follower', but got: {user_follows.text}"

    browser.get(f"{live_server}/user/{user1_username}")

    time.sleep(2)

    user_follows = browser.find_element(By.XPATH, "//p[contains(text(), 'followers')]")
    assert '0 followers' in user_follows.text, f"Expected '0 followers', but got: {user_follows.text}"
    assert '1 following' in user_follows.text, f"Expected '1 following', but got: {user_follows.text}"

    # Unfollow
    browser.get(f"{live_server}/user/{user2_username}")

    time.sleep(2)

    unfollow_button = browser.find_element(By.XPATH, "//input[@type='submit' and @value='Unfollow']")
    unfollow_button.click()

    user_follows = browser.find_element(By.XPATH, "//p[contains(text(), 'followers')]")
    assert '0 followers' in user_follows.text, f"Expected '0 followers', but got: {user_follows.text}"
    assert '0 following' in user_follows.text, f"Expected '0 following', but got: {user_follows.text}"

    browser.get(f"{live_server}/user/{user1_username}")

    time.sleep(2)

    user_follows = browser.find_element(By.XPATH, "//p[contains(text(), 'followers')]")
    assert '0 followers' in user_follows.text, f"Expected '0 followers', but got: {user_follows.text}"
    assert '0 following' in user_follows.text, f"Expected '0 following', but got: {user_follows.text}"
