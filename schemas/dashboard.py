from pydantic import BaseModel


class DashboardResponse(BaseModel):
    employees_total: int
    employees_active: int
    employees_blocked: int
    clients_total: int
    accounts_total: int
    tickets_total: int
    transfers_total: int