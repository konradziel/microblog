from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_registration_flow(live_server, browser):
    username = "testUser"
    email = "testUser@example.com"
    password = "Secret123!"

    browser.get(f"{live_server}/auth/register")

    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    browser.find_element(By.NAME, "username").send_keys(username)
    browser.find_element(By.NAME, "email").send_keys(email)
    browser.find_element(By.NAME, "password").send_keys(password)
    browser.find_element(By.NAME, "password2").send_keys(password)

    browser.find_element(By.CSS_SELECTOR, "input[type=submit],button[type=submit]").click()
    WebDriverWait(browser, 10).until(
        EC.url_contains("/auth/login")
    )

    page = browser.page_source
    assert "Congratulations, you are now a registered user!" in page or "Sign In" in page

def test_login_flow(live_server, browser):
    username = "e2e_login_user"
    email = "e2e_login_user@example.com"
    password = "Secret123!"

    # Najpierw rejestracja użytkownika przez UI (pewny stan)
    browser.get(f"{live_server}/auth/register")
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.NAME, "username")))
    browser.find_element(By.NAME, "username").clear(); browser.find_element(By.NAME, "username").send_keys(username)
    browser.find_element(By.NAME, "email").clear(); browser.find_element(By.NAME, "email").send_keys(email)
    browser.find_element(By.NAME, "password").clear(); browser.find_element(By.NAME, "password").send_keys(password)
    browser.find_element(By.NAME, "password2").clear(); browser.find_element(By.NAME, "password2").send_keys(password)
    browser.find_element(By.CSS_SELECTOR, "input[type=submit],button[type=submit]").click()
    WebDriverWait(browser, 10).until(EC.url_contains("/auth/login"))

    # Teraz logowanie tym użytkownikiem
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.NAME, "username")))
    browser.find_element(By.NAME, "username").clear(); browser.find_element(By.NAME, "username").send_keys(username)
    browser.find_element(By.NAME, "password").clear(); browser.find_element(By.NAME, "password").send_keys(password)
    browser.find_element(By.CSS_SELECTOR, "input[type=submit],button[type=submit]").click()

    # Oczekuj przejścia na stronę główną lub brak formularza logowania
    WebDriverWait(browser, 10).until(lambda d: "/auth/login" not in d.current_url)
    assert "Sign In" not in browser.page_source


