from typing import Optional
from pydantic import BaseModel


class EmployeeResponse(BaseModel):
    id: str
    uuid: str
    email: str
    username: str
    full_name: str
    first_name: str
    last_name: str
    status: str
    is_active: bool
    is_blocked: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    clients_count: int = 0
    tickets_count: int = 0