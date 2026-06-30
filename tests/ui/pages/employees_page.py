from playwright.sync_api import Page


class EmployeesPage:
    URL = "https://student.bank.easyitlab.tech/#/student/employees"

    def __init__(self, page: Page):
        self.page = page

        # Локаторы взяты из реального codegen
        self.add_button = page.get_by_role("main").get_by_role("button", name="Add employee")
        self.full_name_input = page.get_by_role("textbox", name="Иванов Иван")
        self.email_input = page.get_by_role("textbox", name="employee@demobank.local")
        self.password_input = page.get_by_role("textbox", name="Min 8 chars")
        self.create_button = page.get_by_role("button", name="Create")

    def open(self):
        self.page.goto(self.URL)
        self.add_button.wait_for(state="visible")

    def add_employee(self, full_name: str, email: str, password: str):
        self.add_button.click()
        self.full_name_input.fill(full_name)
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.create_button.click()

    def delete_employee_by_row(self):
        self.page.once("dialog", lambda dialog: dialog.accept())
        self.page.get_by_role("button", name="Delete", exact=True).first.click()