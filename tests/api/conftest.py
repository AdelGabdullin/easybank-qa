import pytest
import requests
from utils.auth import get_token
from config.settings import API_URL
from faker import Faker

fake = Faker("ru_RU")


@pytest.fixture(scope="session")
def api_client():
    # Получаем токен один раз
    token = get_token()
    # Создаём сессию
    session = requests.Session()
    # Токен для всех запросов
    session.headers.update({"Authorization": f"Bearer {token}"})

    # Сохраняем base_url прямо в сессии — тесты будут брать отсюда
    session.base_url = API_URL

    return session


@pytest.fixture
def created_employee(api_client):
    email = f"test.{fake.uuid4()[:8]}@demobank.local"
    full_name = fake.name()

    # Пробуем создать сотрудника до 3 раз с паузой
    for attempt in range(3):
        response = api_client.post(
            f"{api_client.base_url}/students/employees",
            json={"email": email, "full_name": full_name, "password": "employee123"}
        )
        if response.status_code == 200:
            break
        time.sleep(1)

    employee = response.json()
    yield employee

    api_client.delete(
        f"{api_client.base_url}/students/employees/{employee['id']}"
    )
