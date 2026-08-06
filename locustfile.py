import random
from typing import Any

from faker import Faker
from locust import HttpUser, between, task

from config.settings import API_URL, LOGIN, PASSWORD


fake = Faker("ru_RU")


def extract_identifier(payload: dict[str, Any]) -> str:
    # В разных ручках API идентификатор может приходить как id или как uuid.
    # Здесь мы забираем то, что есть, чтобы не дублировать эту проверку по всему файлу.
    return payload.get("id") or payload.get("uuid") or ""


class EasyBankStudentUser(HttpUser):
    # Виртуальный пользователь будет делать паузу между запросами от 1 до 3 секунд.
    # Это нужно, чтобы поведение было ближе к реальному пользователю, а не к "пулемёту" без пауз.
    wait_time = between(1, 3)
    host = API_URL

    def on_start(self) -> None:
        # Эти поля пригодятся нам дальше:
        # employee_id нужен для чтения данных сотрудника и списка его клиентов,
        # employee_delete_id нужен для удаления сотрудника в конце сценария.
        self.employee_id = ""
        self.employee_delete_id = ""

        # Каждый виртуальный пользователь сначала логинится.
        # То есть если ты запустишь 10 users, то будет 10 отдельных логинов.
        # Так мы проверяем не только бизнес-ручки, но и то, как система ведёт себя при авторизации.
        login_response = self.client.post(
            "/auth/login",
            json={"email": LOGIN, "password": PASSWORD},
            name="/auth/login",
        )
        login_response.raise_for_status()

        # После логина сохраняем access_token в заголовки.
        # Все следующие запросы этого виртуального пользователя пойдут уже от авторизованного имени.
        token = login_response.json()["access_token"]
        self.client.headers.update({"Authorization": f"Bearer {token}"})

        # Здесь я создаю сотрудника на старте каждого пользователя.
        # Это удобно: потом можно безопасно читать его данные и создавать на него клиентов,
        # не завязываясь на заранее существующие записи в базе.
        employee = self._create_employee()
        self.employee_id = extract_identifier(employee)
        self.employee_delete_id = employee.get("uuid") or self.employee_id

    def on_stop(self) -> None:
        # Когда виртуальный пользователь завершает работу, стараемся убрать за собой данные.
        # Это важная привычка в нагрузочном тестировании на тестовых стендах:
        # не засорять базу временными сущностями после каждого прогона.
        if not self.employee_delete_id:
            return

        self.client.delete(
            f"/students/employees/{self.employee_delete_id}",
            name="/students/employees/[employee_id] DELETE",
        )

    def _create_employee(self) -> dict[str, Any]:
        # Делаем уникальные данные, чтобы тесты не падали из-за конфликтов одинаковых email.
        email = f"load.{fake.uuid4()[:8]}@demobank.local"
        full_name = fake.name()

        # Это подготовительный запрос.
        # Он не столько "нагружает" систему, сколько подготавливает тестовые данные для следующих шагов.
        response = self.client.post(
            "/students/employees",
            json={
                "email": email,
                "full_name": full_name,
                "password": "employee123",
            },
            name="/students/employees POST",
        )
        response.raise_for_status()
        return response.json()

    @task(5)
    def dashboard(self) -> None:
        # Этот запрос я запускаю с большим весом task(5),
        # потому что чтение dashboard обычно происходит чаще, чем сложные CRUD-операции.
        # На практике это значит: Locust будет выбирать эту задачу чаще остальных.
        self.client.get("/students/dashboard", name="/students/dashboard")

    @task(3)
    def employee_details(self) -> None:
        # Здесь мы читаем карточку уже созданного сотрудника.
        # Такой запрос помогает посмотреть, как API держит простые GET-запросы под умеренной нагрузкой.
        if not self.employee_id:
            return
        self.client.get(
            f"/students/employees/{self.employee_id}",
            name="/students/employees/[employee_id] GET",
        )

    @task(2)
    def employee_clients(self) -> None:
        # Здесь читаем список клиентов конкретного сотрудника.
        # Если потом у тебя будет полная структура API, мы сможем решить,
        # подходит ли эта ручка для чтения под нагрузкой или лучше выбрать другую.
        if not self.employee_id:
            return
        self.client.get(
            f"/students/employees/{self.employee_id}/clients",
            name="/students/employees/[employee_id]/clients GET",
        )

    @task(1)
    def create_and_cleanup_client_flow(self) -> None:
        # А это уже небольшой write-сценарий.
        # Он выполняется реже остальных, потому что запись в систему обычно тяжелее чтения.
        # Здесь идея такая:
        # 1. создаём клиента,
        # 2. создаём ему счёт,
        # 3. блокируем счёт,
        # 4. удаляем всё обратно.
        #
        # Важно: этот код НЕ означает "делаю 10 клиентов в секунду".
        # Скорость зависит от общего числа users, spawn rate, wait_time и времени ответа сервера.
        # Например, если ты поставишь 10 users, тогда 10 виртуальных пользователей будут параллельно
        # крутить такие шаги, и уже это даст нагрузку на API.
        if not self.employee_id:
            return

        email = f"client.{fake.uuid4()[:8]}@demobank.local"
        client_payload = {
            "email": email,
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "phone": fake.phone_number(),
            "student_username": email,
        }

        # Создаём клиента на сотрудника.
        # Это хороший пример POST-запроса для нагрузки на создание сущностей.
        client_response = self.client.post(
            f"/students/employees/{self.employee_id}/clients",
            json=client_payload,
            name="/students/employees/[employee_id]/clients POST",
        )
        if client_response.status_code not in (200, 201):
            client_response.failure(f"Unexpected status: {client_response.status_code}")
            return

        client_data = client_response.json()
        client_id = extract_identifier(client_data)
        account_id = ""

        try:
            # Теперь создаём счёт клиенту.
            # Здесь можно увидеть, как приложение ведёт себя на цепочке связанных операций,
            # а не только на одном одиночном запросе.
            account_response = self.client.post(
                f"/students/clients/{client_id}/accounts",
                json={"currency": "RUB", "type": random.choice(["CURRENT", "SAVINGS"])},
                name="/students/clients/[client_id]/accounts POST",
            )
            if account_response.status_code not in (200, 201):
                account_response.failure(
                    f"Unexpected status: {account_response.status_code}"
                )
                return

            account_data = account_response.json()
            account_id = extract_identifier(account_data)

            # После создания счёта сразу пробуем ещё одно действие над ним.
            # Это полезно для сценария "создали сущность -> сразу работаем с ней дальше".
            self.client.patch(
                f"/students/accounts/{account_id}/block",
                name="/students/accounts/[account_id]/block PATCH",
            )
        finally:
            # Даже если что-то пошло не так на одном из шагов,
            # всё равно стараемся выполнить очистку через finally.
            # Это делает сценарий аккуратнее и безопаснее для тестового стенда.
            if account_id:
                self.client.delete(
                    f"/students/accounts/{account_id}",
                    name="/students/accounts/[account_id] DELETE",
                )
            if client_id:
                self.client.delete(
                    f"/students/clients/{client_id}",
                    params={"force": True},
                    name="/students/clients/[client_id] DELETE",
                )
