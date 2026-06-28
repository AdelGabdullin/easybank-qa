import pytest
import requests
from utils.auth import get_token
from config.settings import API_URL

@pytest.fixture
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

