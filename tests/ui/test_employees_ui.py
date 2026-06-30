import allure
from playwright.sync_api import expect
from faker import Faker
from tests.ui.pages.employees_page import EmployeesPage

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