import pytest
from playwright.sync_api import Page
from config.settings import LOGIN, PASSWORD
from tests.ui.pages.login_page import LoginPage


@pytest.fixture(scope="session")
def aauthenticated_page(browser):
    # Создаём новую страницу в браузере
    page = browser.new_page()
    # Создаём объект страницы логина
    login_page = LoginPage(page)
    # Открываем страницу и логинимся
    login_page.open()
    login_page.login(LOGIN, PASSWORD)
    # Ждём что появится дашборд — значит логин прошёл успешно
    page.wait_for_url("**/student/dashboard")

    # Возвращаем залогиненную страницу для всех UI тестов
    return page