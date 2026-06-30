import allure
from playwright.sync_api import expect
from faker import Faker
from tests.ui.pages.employees_page import EmployeesPage
import pytest

fake = Faker("ru_RU")


@allure.feature("Employees UI")
@allure.title("Создание сотрудника через UI")
def test_create_employee_ui(authenticated_page):
    page = authenticated_page
    employees_page = EmployeesPage(page)

    full_name = fake.name()
    email = f"test.{fake.uuid4()[:8]}@demobank.local"

    with allure.step("Открываем страницу сотрудников"):
        employees_page.open()

    with allure.step("Создаём нового сотрудника"):
        employees_page.add_employee(full_name, email, "employee123")

    with allure.step("Проверяем что сотрудник появился"):
        expect(page.get_by_role("main")).to_contain_text(email)

@pytest.mark.xfail(reason="BUG: фронт отправляет st-XXXX вместо UUID в bulk-delete")
@allure.feature("Employees UI")
@allure.title("BUG: удаление сотрудника через UI отправляет неверный формат ID")
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_employee_sends_invalid_id_bug(authenticated_page):
    page = authenticated_page
    employees_page = EmployeesPage(page)

    with allure.step("Открываем страницу сотрудников"):
        employees_page.open()

    with allure.step("Удаляем сотрудника через кнопку в строке и перехватываем запрос"):
        with page.expect_response(lambda r: "bulk-delete" in r.url) as response_info:
            page.once("dialog", lambda dialog: dialog.accept())
            page.get_by_role("button", name="Delete", exact=True).first.click()

    with allure.step("Проверяем что удаление прошло успешно"):
        response = response_info.value
        # Ожидаем 200 — но сейчас сервер возвращает 400 из-за бага
        assert response.status == 200