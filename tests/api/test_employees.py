import allure
from faker import Faker
from schemas.employee import EmployeeResponse

fake = Faker("ru_RU")

employee_data = {}


@allure.feature("Employees")
@allure.story("CRUD")
@allure.title("Создание сотрудника")
def test_create_employee(api_client):
    with allure.step("Генерируем данные сотрудника"):
        email = f"test.{fake.uuid4()[:8]}@demobank.local"
        full_name = fake.name()
        employee_data["email"] = email

    with allure.step("Отправляем POST запрос на создание сотрудника"):
        response = api_client.post(
            f"{api_client.base_url}/students/employees",
            json={"email": email, "full_name": full_name, "password": "employee123"}
        )

    with allure.step("Проверяем статус код 200"):
        assert response.status_code == 200

    with allure.step("Валидируем схему ответа через Pydantic"):
        employee = EmployeeResponse(**response.json())

    with allure.step("Проверяем бизнес-логику"):
        assert employee.email == email
        assert employee.full_name == full_name
        assert len(employee.email) > 0
        assert len(employee.full_name) > 0
        assert not (employee.is_active and employee.is_blocked)
        assert employee.clients_count >= 0
        assert employee.tickets_count >= 0
        employee_data["id"] = employee.id


@allure.feature("Employees")
@allure.story("CRUD")
@allure.title("Получение созданного сотрудника")
def test_get_employee(api_client):
    with allure.step("Отправляем GET запрос на получение сотрудника по id"):
        response = api_client.get(
            f"{api_client.base_url}/students/employees/{employee_data['id']}"
        )

    with allure.step("Проверяем статус код 200"):
        assert response.status_code == 200

    with allure.step("Валидируем схему ответа через Pydantic"):
        employee = EmployeeResponse(**response.json())

    with allure.step("Проверяем что получили именно созданного сотрудника"):
        assert employee.email == employee_data["email"]
        assert len(employee.full_name) > 0
        assert not (employee.is_active and employee.is_blocked)
        assert employee.clients_count >= 0
        assert employee.tickets_count >= 0


@allure.feature("Employees")
@allure.story("CRUD")
@allure.title("Изменение созданного сотрудника")
def test_update_employee(api_client):
    with allure.step("Генерируем новые данные для обновления"):
        new_full_name = fake.name()
        new_email = f"updated.{fake.uuid4()[:8]}@demobank.local"

    with allure.step("Делаем PATCH запрос на изменение сотрудника по id"):
        response = api_client.patch(
            f"{api_client.base_url}/students/employees/{employee_data['id']}",
            json={"email": new_email, "full_name": new_full_name}
        )

    with allure.step("Проверяем статус код 200"):
        assert response.status_code == 200

    with allure.step("Валидируем схему ответа через Pydantic"):
        employee = EmployeeResponse(**response.json())

    with allure.step("Проверяем что данные действительно обновились"):
        assert employee.full_name == new_full_name
        assert employee.email == new_email
        assert not (employee.is_active and employee.is_blocked)


@allure.feature("Employees")
@allure.story("CRUD")
@allure.title("Удаление созданного сотрудника")
def test_delete_employee(api_client):
    with allure.step("Делаем DELETE запрос по id сотрудника"):
        response = api_client.delete(
            f"{api_client.base_url}/students/employees/{employee_data['id']}"
        )

    with allure.step("Проверяем статус код 200"):
        assert response.status_code == 200

    with allure.step("Проверяем что сотрудник действительно удалён — GET должен вернуть 404"):
        check = api_client.get(
            f"{api_client.base_url}/students/employees/{employee_data['id']}"
        )
        assert check.status_code == 404