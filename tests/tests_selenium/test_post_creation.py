import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tests.conftest import register_user, login_user

def test_post_creation_flow(live_server, browser):
    user_username = "post_creation_user"
    user_email = "post_creation_user@example.com"
    user_password = "Secret123!"
    post_content = "This is a test post"
    
    register_user(browser, live_server, user_username, user_email, user_password)
    login_user(browser, live_server, user_username, user_password)

    post_field = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, "//textarea[@name='post']"))
    )
    post_field.clear()
    post_field.send_keys(post_content)
    
    submit_button = browser.find_element(By.XPATH, "//input[@type='submit']")
    submit_button.click()
    
    time.sleep(2)

    assert post_content in browser.page_source