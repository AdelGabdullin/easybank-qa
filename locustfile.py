from typing import Any

from faker import Faker
from locust import HttpUser, SequentialTaskSet, between, task

from config.settings import API_URL, LOGIN, PASSWORD


fake = Faker("ru_RU")


def extract_identifier(payload: dict[str, Any]) -> str:
    return payload.get("id") or payload.get("uuid") or ""


class EmployeeCrudFlow(SequentialTaskSet):
    def on_start(self) -> None:
        self.employee_id = ""
        self.employee_delete_id = ""
        self.employee_email = ""

    def _create_employee_payload(self) -> dict[str, str]:
        return {
            "email": f"load.{fake.uuid4()[:8]}@demobank.local",
            "full_name": fake.name(),
            "password": "employee123",
        }

    @task
    def create_employee(self) -> None:
        # Первый шаг потока: создаём сотрудника, с которым дальше будем работать.
        payload = self._create_employee_payload()
        response = self.client.post(
            "/students/employees",
            json=payload,
            name="/students/employees POST",
        )
        response.raise_for_status()

        employee = response.json()
        self.employee_id = extract_identifier(employee)
        self.employee_delete_id = employee.get("uuid") or self.employee_id
        self.employee_email = employee.get("email", payload["email"])

    @task
    def get_employee(self) -> None:
        # После создания читаем карточку сотрудника и смотрим, что сущность доступна.
        if not self.employee_id:
            return

        self.client.get(
            f"/students/employees/{self.employee_id}",
            name="/students/employees/[employee_id] GET",
        )

    @task
    def update_employee(self) -> None:
        # Меняем данные того же сотрудника, чтобы в сценарии был шаг Update.
        if not self.employee_id:
            return

        new_email = f"updated.{fake.uuid4()[:8]}@demobank.local"
        new_full_name = fake.name()

        response = self.client.patch(
            f"/students/employees/{self.employee_id}",
            json={"email": new_email, "full_name": new_full_name},
            name="/students/employees/[employee_id] PATCH",
        )
        response.raise_for_status()

        self.employee_email = new_email

    @task
    def list_employees(self) -> None:
        # Дополнительно читаем общий список сотрудников, чтобы увидеть чтение списка в CRUD-цепочке.
        self.client.get("/students/employees", name="/students/employees GET")

    @task
    def delete_employee(self) -> None:
        # Завершаем цикл удалением сотрудника. После этого поток начнётся заново с Create.
        if not self.employee_delete_id:
            return

        response = self.client.delete(
            f"/students/employees/{self.employee_delete_id}",
            name="/students/employees/[employee_id] DELETE",
        )
        response.raise_for_status()

        self.employee_id = ""
        self.employee_delete_id = ""
        self.employee_email = ""

    def on_stop(self) -> None:
        # Если пользователь остановился посередине цикла, пытаемся дочистить остаток.
        if not self.employee_delete_id:
            return

        self.client.delete(
            f"/students/employees/{self.employee_delete_id}",
            name="/students/employees/[employee_id] DELETE cleanup",
        )


class EasyBankStudentUser(HttpUser):
    wait_time = between(1, 3)
    host = API_URL
    tasks = [EmployeeCrudFlow]

    def on_start(self) -> None:
        # Каждый виртуальный пользователь сначала получает собственный токен.
        login_response = self.client.post(
            "/auth/login",
            json={"email": LOGIN, "password": PASSWORD},
            name="/auth/login",
        )
        login_response.raise_for_status()

        token = login_response.json()["access_token"]
        self.client.headers.update({"Authorization": f"Bearer {token}"})
