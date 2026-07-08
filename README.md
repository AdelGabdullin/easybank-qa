# EasyBank QA

Проект автоматизированного тестирования демо-банковского приложения [EasyBank](https://student.bank.easyitlab.tech).

## Стек

- Python 3.12
- pytest
- requests
- Playwright
- Allure
- Docker
- GitHub Actions
- Pydantic
- pytest-xdist

## Структура проекта

```
easybank-qa/
├── .github/
│   └── workflows/
│       └── tests.yml        # CI/CD pipeline
├── config/
│   └── settings.py          # настройки окружения
├── tests/
│   ├── api/
│   │   ├── conftest.py      # фикстура api_client
│   │   ├── test_dashboard.py
│   │   └── test_employees.py
│   └── ui/
│       ├── conftest.py      # фикстура authenticated_page
│       ├── pages/
│       │   ├── login_page.py
│       │   └── employees_page.py
│       ├── test_dashboard_ui.py
│       └── test_employees_ui.py
        └── test_client.py 
├── utils/
│   └── auth.py              # получение токена авторизации
├── .env.example
├── .gitignore
├── Dockerfile
├── pytest.ini
└── requirements.txt
```

## Покрытие

| Модуль | Тип | Тесты |
|---|---|---|
| Dashboard | API | статус 200, наличие полей |
| Employees | API | CRUD (создание, получение, обновление, удаление) |
| Clients | API | полный цикл: создание сотрудника → создание клиента → создание счёта → блокировка счёта → удаление счёта → удаление клиента |
| Dashboard | UI | отображение карточек статистики |
| Employees | UI | создание через форму |
| Employees | UI | баг: удаление через UI (xfail) |
| Employees | API | Pydantic валидация схемы + бизнес-логика |

## Локальный запуск

**Требования:** Python 3.12, pip

```bash
git clone https://github.com/AdelGabdullin/easybank-qa.git
cd easybank-qa

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
playwright install chromium
```

Создать файл `.env` на основе `.env.example` и заполнить данными.

```bash
# Все тесты
python -m pytest tests/ -v

# Только API
python -m pytest tests/api/ -v

# Только UI
python -m pytest tests/ui/ -v

# С Allure отчётом
python -m pytest tests/ -v --alluredir=allure-results
allure serve allure-results
```

## Запуск в Docker

```bash
docker build -t easybank-qa .
docker run --env-file .env easybank-qa python -m pytest tests/ -v
```

## CI/CD

GitHub Actions запускает тесты автоматически при push в `main` и при создании Pull Request.

Результаты каждого запуска сохраняются как артефакт `allure-results` во вкладке Actions.

## Известные баги

| ID | Модуль | Описание | Статус |
|---|---|---|---|
| BUG-001 | Employees UI | Удаление сотрудников через UI не работает. Фронт отправляет `st-XXXX` вместо UUID в эндпоинт `bulk-delete`. Затрагивает все способы удаления кроме "Delete all". | Open |
| BUG-002 | Employees API | `DELETE /students/employees/{employee_id}` не удаляет сотрудника при передаче поля `id` (короткий формат, напр. `st-0476`) — требуется `uuid`. Тот же класс проблемы, что в BUG-001 (путаница id/uuid), но на другом эндпоинте. | Обходится в тестах (используем `uuid`) |
| BUG-003 | Clients API | `DELETE /students/clients/{client_id}` без параметра `force=true` удаляет только бизнес-объект клиента, но не связанную учётную запись (`student_user`) — она остаётся висеть и отображается во вкладке "Сотрудники". | Обходится в тестах (`params={"force": True}`) |