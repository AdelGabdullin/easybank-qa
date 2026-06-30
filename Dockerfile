# Базовый образ с Python 3.12
FROM python:3.12-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем браузер для Playwright
RUN playwright install chromium
RUN playwright install-deps chromium

# Копируем весь проект в контейнер
COPY . .

# Команда по умолчанию — запуск всех тестов
CMD ["python", "-m", "pytest", "tests/", "-v", "--alluredir=allure-results"]