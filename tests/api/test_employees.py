import pytest
from faker import Faker
# Создаём объект Faker с русской локалью
fake = Faker("ru_RU")


from faker import Faker

fake = Faker("ru_RU")

# Словарь для хранения данных между тестами
employee_data = {}


def test_create_employee(api_client):
    email = f"test.{fake.uuid4()[:8]}@demobank.local"
    full_name = fake.name()

    response = api_client.post(
        f"{api_client.base_url}/students/employees",
        json={
            "email": email,
            "full_name": full_name,
            "password": "employee123"
        }
    )

    assert response.status_code == 200

    data = response.json()
    assert "id" in data

    # Сохраняем для следующих тестов
    employee_data["id"] = data["id"]
    employee_data["email"] = email


def test_get_employee(api_client):
    response = api_client.get(
        f"{api_client.base_url}/students/employees/{employee_data['id']}"
    )

    assert response.status_code == 200

    data = response.json()
    assert data["email"] == employee_data["email"]

def test_update_employee(api_client):
    # Генерируем новые данные для обновления
    new_full_name = fake.name()
    new_email = f"updated.{fake.uuid4()[:8]}@demobank.local"

    response = api_client.patch(
        f"{api_client.base_url}/students/employees/{employee_data['id']}",
        json={
            "email": new_email,
            "full_name": new_full_name
        }
    )

    assert response.status_code == 200

    data = response.json()
    # Проверяем что данные действительно обновились
    assert data["full_name"] == new_full_name
    assert data["email"] == new_email


def test_delete_employee(api_client):
    response = api_client.delete(
        f"{api_client.base_url}/students/employees/{employee_data['id']}"
    )

    assert response.status_code == 200

    # Проверяем что сотрудник действительно удалён — сервер должен вернуть 404
    check = api_client.get(
        f"{api_client.base_url}/students/employees/{employee_data['id']}"
    )
    assert check.status_code == 404