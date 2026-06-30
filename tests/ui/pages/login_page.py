from playwright.sync_api import Page

class LoginPage:
    #URL страницы логина
    URL = "https://student.bank.easyitlab.tech/#/login"
    def __init__(self, page: Page):
        # page — это объект браузера который передаёт Playwright
        self.page = page
        # Находим поля по type атрибуту
        self.email_input = page.locator('input[type="email"]')
        self.password_input = page.locator('input[type="password"]')
        # Кнопку находим по тексту
        self.submit_button = page.locator("button").first

    def open(self):
        # Открываем страницу логина в браузере
        self.page.goto(self.URL)

    def login(self, email: str, password: str):
        # Вводим email, пароль и нажимаем войти
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.submit_button.wait_for(state="visible")
        self.submit_button.click()