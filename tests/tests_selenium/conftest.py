import pytest
import socket
import threading
import time
from selenium import webdriver
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