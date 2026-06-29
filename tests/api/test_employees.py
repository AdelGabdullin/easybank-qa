import allure
from faker import Faker
# Создаём объект Faker с русской локалью
fake = Faker("ru_RU")

# Словарь для хранения данных между тестами
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

    with allure.step("Проверяем статус код и сохраняем id"):
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        employee_data["id"] = data["id"]

@allure.feature("Employees")
@allure.story("CRUD")
@allure.title("Получение созданного сотрудника")
def test_get_employee(api_client):
    with allure.step("Отправляем GET запрос на получение сотрудника по id"):
        response = api_client.get(
            f"{api_client.base_url}/students/employees/{employee_data['id']}"
    )

    with allure.step("Проверяем что статус код 200"):
        assert response.status_code == 200

    with allure.step("Проверяем что email cоответствует созданному сотруднику"):
        data = response.json()
        assert data["email"] == employee_data["email"]


@allure.feature("Employees")
@allure.story("CRUD")
@allure.title("Изменение созданного сотрудника")
def test_update_employee(api_client):
    with allure.step("Генерируем новые данные для обновления"):
        new_full_name = fake.name()
        new_email = f"updated.{fake.uuid4()[:8]}@demobank.local"
    with allure.step("Делаем patch запрос на изменение по id "):
        response = api_client.patch(
        f"{api_client.base_url}/students/employees/{employee_data['id']}",
        json={
            "email": new_email,
            "full_name": new_full_name
        }
    )
    with allure.step("Проверяем статус код 200"):
        assert response.status_code == 200
    with allure.step("Проверяем что данные действительно обновились"):
        data = response.json()
        assert data["full_name"] == new_full_name
        assert data["email"] == new_email

@allure.feature("Employees")
@allure.story("CRUD")
@allure.title("Удаление созданного сотрудника")
def test_delete_employee(api_client):
    with allure.step("Делаем delete запрос по id сотрудника"):
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