from playwright.sync_api import Page

class LoginPage:
    #URL страницы логина
    URL = "https://student.bank.easyitlab.tech/#/login"
    def __init__(self, page: Page):
        # page — это объект браузера который передаёт Playwright
        self.page = Page
        self.email_input = page.get_by_label("Email")
        self.password_input = page.get_by_label("Пароль")
        self.submit_button = page.get_by_role("button", name="Войти")

    def open(self):
        # Открываем страницу логина в браузере
        self.page.goto(self.URL)

    def login(self, email: str, password: str):
        # Вводим email, пароль и нажимаем войти
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.submit_button.click()