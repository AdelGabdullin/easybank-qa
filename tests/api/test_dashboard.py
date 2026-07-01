import allure
from schemas.dashboard import DashboardResponse

@allure.feature("Dashboard")
def test_dashboard_returns_200(api_client):

    with allure.step("Отправляем GET запрос на dashboard"):
        response = api_client.get(f"{api_client.base_url}/students/dashboard")

    with allure.step("Проверяем статус код 200"):
        assert response.status_code == 200

    with allure.step("Валидируем схему ответа через Pydantic"):
        dashboard = DashboardResponse(**response.json())

    with allure.step("Проверяем бизнес-логику полей"):
        # Все счётчики не могут быть отрицательными
        assert dashboard.employees_total >= 0
        assert dashboard.employees_active >= 0
        assert dashboard.employees_blocked >= 0
        assert dashboard.clients_total >= 0
        assert dashboard.accounts_total >= 0
        assert dashboard.tickets_total >= 0
        assert dashboard.transfers_total >= 0

        # Активных и заблокированных не может быть больше чем всего сотрудников
        assert dashboard.employees_active <= dashboard.employees_total
        assert dashboard.employees_blocked <= dashboard.employees_total

        # Сумма активных и заблокированных не превышает общее количество
        assert dashboard.employees_active + dashboard.employees_blocked <= dashboard.employees_total