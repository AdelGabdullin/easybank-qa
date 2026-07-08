import pytest
import requests
import time
from utils.auth import get_token
from config.settings import API_URL
from faker import Faker

fake = Faker("ru_RU")

# Создаю сессию студента
@pytest.fixture(scope="session")

def api_client():
    token = get_token()
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {token}"})
    session.base_url = API_URL

    return session

# Создаю сотрудника
@pytest.fixture(scope="session")

def created_employee(api_client):
    email = f"test.{fake.uuid4()[:8]}@demobank.local"
    full_name = fake.name()
    password = fake.password(length=10, special_chars=False, digits=True, upper_case=True, lower_case=True)


    for attempt in range(3):
        response = api_client.post(
            f"{api_client.base_url}/students/employees",
            json={"email": email, "full_name": full_name, "password": password}
        )
        if response.status_code == 200:
            break
        time.sleep(1)

    employee = response.json()
    employee["password"] = password
    yield employee

    delete_response = api_client.delete(
        f"{api_client.base_url}/students/employees/{employee['uuid']}"
    )




# #Логинюсь созданным сотрудником и отдаю сессию с его токеном
# @pytest.fixture(scope="session")
#
# def employee_client(created_employee, api_client):
#     response = requests.post(f"{API_URL}/auth/login", json={"email": created_employee["email"], "password": created_employee["password"]}, headers=api_client.headers)
#     token = response.json()["access_token"]
#     session = requests.Session()
#     session.headers.update({"Authorization": f"Bearer {token}"})
#     session.base_url = API_URL
#     yield session

