import allure


@allure.feature("Dashboard")
def test_dashboard_returns_200(api_client):

    with allure.step("Отправляем GET запрос на dashboard"):
        response = api_client.get(f"{api_client.base_url}/students/dashboard")

    with allure.step("Проверяем статус код 200"):
        assert response.status_code == 200

    with allure.step("Проверяем что в ответе есть нужные поля"):
        data = response.json()
        assert "employees_total" in data
        assert "clients_total" in data
        assert "accounts_total" in data