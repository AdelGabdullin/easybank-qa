import pytest
import requests

from tests.api.conftest import api_client
from utils.auth import get_token



def test_dashboard_returns_200(api_client):
    # api_client — это наша фикстура из conftest.py
    # pytest сам её найдёт и передаст в тест
    # Отправляем GET запрос на dashboard
    # В заголовке передаём токен — без него сервер вернёт 401
    response = api_client.get(f"{api_client.base_url}/students/dashboard")
    # Проверяем что сервер ответил 200
    assert response.status_code == 200
    # Преобразуем ответ в словарь
    data = response.json()
    # Проверяем что в ответе есть нужные поля
    assert "employees_total" in data
    assert "clients_total" in data
    assert "accounts_total" in data