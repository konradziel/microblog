import pytest
import socket
import threading
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from config import Config
from app import create_app, db
from app.models import User


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    ELASTICSEARCH_URL = None


@pytest.fixture(scope="session")
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def user_create(app):
    def _create(username='apitest', email='api@example.com', password='pass'):
        with app.app_context():
            u = User(username=username, email=email)
            u.set_password(password)
            db.session.add(u)
            db.session.commit()
            return u.id
    return _create


@pytest.fixture()
def user_id(user_create):
    return user_create()


@pytest.fixture()
def auth_headers(app, user_id):
    with app.app_context():
        u = db.session.get(User, user_id)
        token = u.get_token()
        db.session.commit()
    return {"Authorization": f"Bearer {token}"}


def _free_port() -> int:
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.fixture(scope="session")
def live_server(app):
    from werkzeug.serving import make_server
    port = _free_port()
    server = make_server('127.0.0.1', port, app)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{port}"
    # prosta pauza na start serwera
    time.sleep(0.5)
    yield base_url
    server.shutdown()
    thread.join(timeout=2)


@pytest.fixture(scope="session")
def browser():
    """Headless Firefox (geckodriver przez selenium-manager)."""
    opts = FirefoxOptions()
    # opts.add_argument("-headless")
    driver = webdriver.Firefox(options=opts)
    # krótkie timeouts, by nie wisieć
    driver.set_page_load_timeout(10)
    driver.implicitly_wait(2)
    yield driver
    driver.quit()


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