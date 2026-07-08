import requests
import allure
from faker import Faker
fake = Faker("ru_RU")




def test_employee_client_authorized(api_client, created_employee):
    with allure.step("Проверка доступа к клиентам сотрудника через студенческий токен"):
        response = api_client.get(
            f"{api_client.base_url}/students/employees/{created_employee['id']}/clients"
        )
        with allure.step("Проверка статус кода 200"):
            assert response.status_code == 200


def test_create_client_success(created_employee, api_client):
    email = f"client.{fake.uuid4()[:8]}@demobank.local"
    first_name = fake.first_name()
    last_name = fake.last_name()
    phone = fake.phone_number()
    with allure.step("Создание клиента"):
        response = api_client.post(f"{api_client.base_url}/students/employees/{created_employee['id']}/clients", json={
        "email": email, "first_name": first_name, "last_name": last_name, "phone": phone, "student_username": email})

    client_data = response.json()

    with allure.step("Проверка ответа"):
        assert response.status_code in (200,201)
        assert client_data['email'] == email

    with allure.step("Удаление клиента"):
        api_client.delete(f"{api_client.base_url}/students/clients/{client_data['id']}", params={"force": True})


def test_create_account_success(created_employee, api_client):
    email = f"client.{fake.uuid4()[:8]}@demobank.local"
    first_name = fake.first_name()
    last_name = fake.last_name()
    phone = fake.phone_number()
    with allure.step("Создание клиента"):
        response = api_client.post(
            f"{api_client.base_url}/students/employees/{created_employee['id']}/clients", json={
                "email": email, "first_name": first_name, "last_name": last_name, "phone": phone,
                "student_username": email})

    client_data = response.json()
    with allure.step("Проверка ответа"):
        assert response.status_code in (200,201)
        assert client_data['email'] == email

    with allure.step("Создание счета"):
        response = api_client.post(f"{api_client.base_url}/students/clients/{client_data['id']}/accounts", json={"currency": "RUB", "type": "CURRENT"})
        account_data = response.json()

    try:
        with allure.step("Проверка счета"):
            assert response.status_code in (200, 201)
            assert account_data['currency'] == "RUB"
    finally:
        with allure.step("Удаление счета и клиента"):
            api_client.delete(f"{api_client.base_url}/students/accounts/{account_data['id']}")
            api_client.delete(f"{api_client.base_url}/students/clients/{client_data['id']}", params={"force": True})

def test_block_account_success(api_client, created_employee):
    email = f"client.{fake.uuid4()[:8]}@demobank.local"
    first_name = fake.first_name()
    last_name = fake.last_name()
    phone = fake.phone_number()
    with allure.step("Создание клиента для теста"):
        response = api_client.post(
            f"{api_client.base_url}/students/employees/{created_employee['id']}/clients", json={
                "email": email, "first_name": first_name, "last_name": last_name, "phone": phone,
                "student_username": email})

    client_data = response.json()

    with allure.step("Создание счета для теста"):
        response = api_client.post(f"{api_client.base_url}/students/clients/{client_data['id']}/accounts",
                                   json={"currency": "RUB", "type": "CURRENT"})
        account_data = response.json()

    with allure.step("Блокировка счёта"):
        response = api_client.patch(f"{api_client.base_url}/students/accounts/{account_data['id']}/block")

    try:
        with allure.step("Проверка что статус BLOCKED "):
            assert response.status_code == 200
            assert response.json()["status"] == "BLOCKED"
    finally:
        with allure.step("Удаление счета и клиента"):
            api_client.delete(f"{api_client.base_url}/students/accounts/{account_data['id']}")
            api_client.delete(f"{api_client.base_url}/students/clients/{client_data['id']}", params={"force": True})



def test_delete_account_success(api_client, created_employee):
    email = f"client.{fake.uuid4()[:8]}@demobank.local"
    first_name = fake.first_name()
    last_name = fake.last_name()
    phone = fake.phone_number()
    with allure.step("Создание клиента для теста"):
        response = api_client.post(
            f"{api_client.base_url}/students/employees/{created_employee['id']}/clients", json={
                "email": email, "first_name": first_name, "last_name": last_name, "phone": phone,
                "student_username": email})

    client_data = response.json()


    with allure.step("Создание счета для теста"):
        response = api_client.post(f"{api_client.base_url}/students/clients/{client_data['id']}/accounts",
                                   json={"currency": "RUB", "type": "CURRENT"})
        account_data = response.json()

    with allure.step("Удаление счета"):
        response = api_client.delete(f"{api_client.base_url}/students/accounts/{account_data['id']}")

    with allure.step("Проверка статус кода 200"):
        assert response.status_code == 200

    with allure.step("Проверка что счет удален"):
        check_response = api_client.delete(f"{api_client.base_url}/students/accounts/{account_data['id']}")
        assert check_response.status_code == 404

    with allure.step("Удаление клиента"):
        api_client.delete(f"{api_client.base_url}/students/clients/{client_data['id']}", params={"force": True})


def test_delete_client_success(api_client, created_employee):
    email = f"client.{fake.uuid4()[:8]}@demobank.local"
    first_name = fake.first_name()
    last_name = fake.last_name()
    phone = fake.phone_number()
    with allure.step("Создание клиента "):
        response = api_client.post(
            f"{api_client.base_url}/students/employees/{created_employee['id']}/clients", json={
                "email": email, "first_name": first_name, "last_name": last_name, "phone": phone,
                "student_username": email})

    client_data = response.json()

    with allure.step("Удаление клиента"):
        response = api_client.delete(f"{api_client.base_url}/students/clients/{client_data['id']}", params={"force": True})
        assert response.status_code == 200

    with allure.step("Проверка удаления клиента"):
        response = api_client.get(f"{api_client.base_url}/students/clients/{client_data['id']}")
        assert response.status_code == 404






















