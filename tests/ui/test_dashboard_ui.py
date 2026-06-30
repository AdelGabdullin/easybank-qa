import allure
from playwright.sync_api import expect


@allure.feature("Dashboard UI")
@allure.title("Дашборд отображает карточки со статистикой")
def test_dashboard_cards_visible(authenticated_page):
    page = authenticated_page

    with allure.step("Переходим на дашборд"):
        page.goto("https://student.bank.easyitlab.tech/#/student/dashboard")

    with allure.step("Проверяем что карточки статистики видны"):
        expect(page.get_by_text("Total Employees")).to_be_visible()
        expect(page.get_by_text("Total Clients")).to_be_visible()
        expect(page.get_by_text("Total Accounts")).to_be_visible()