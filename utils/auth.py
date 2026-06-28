import requests
from config.settings import API_URL, LOGIN, PASSWORD


def get_token() ->str:
    # Отправляем POST запрос на эндпоинт логина
    # В теле передаём email и пароль
    response = requests.post(
    url=f"{API_URL}/auth/login",
    json={"email": LOGIN, "password": PASSWORD}
)
# Проверяем что сервер ответил успешно (статус 200)
# Если нет — pytest сразу упадёт с понятной ошибкой
    response.raise_for_status()
    return response.json()["access_token"]
