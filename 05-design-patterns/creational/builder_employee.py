"""Builder pattern - refactor of the HR employee onboarding system.

Problems of the original code:
- 17 positional parameters: one missing None shifts every following argument
- `False, True, True, True` means nothing when reading the call
- validation scattered, presets (a developer always has a laptop + VPN) not enforced
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Employee:
    """The product: a simple data container."""
    first_name: str
    last_name: str
    email: str
    department: str
    position: str
    salary: float
    start_date: Optional[str]
    manager_id: Optional[int] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    has_parking: bool = False
    has_laptop: bool = False
    has_vpn_access: bool = False
    has_admin_rights: bool = False
    office_location: Optional[str] = None
    contract_type: str = "permanent"


class EmployeeBuilder:
    """Builds an Employee step by step. Each method returns self so calls can be chained."""

    def __init__(self):
        self._data = {"start_date": None, "salary": 0.0}

    def with_name(self, first_name: str, last_name: str) -> "EmployeeBuilder":
        self._data.update(first_name=first_name, last_name=last_name)
        return self

    def with_email(self, email: str) -> "EmployeeBuilder":
        self._data["email"] = email
        return self

    def with_job(self, department: str, position: str, salary: float) -> "EmployeeBuilder":
        self._data.update(department=department, position=position, salary=salary)
        return self

    def starting_on(self, start_date: str) -> "EmployeeBuilder":
        self._data["start_date"] = start_date
        return self

    def with_manager(self, manager_id: int) -> "EmployeeBuilder":
        self._data["manager_id"] = manager_id
        return self

    def with_contact(self, phone: Optional[str] = None, address: Optional[str] = None,
                     emergency_contact: Optional[str] = None) -> "EmployeeBuilder":
        self._data.update(phone=phone, address=address, emergency_contact=emergency_contact)
        return self

    def with_equipment(self, laptop: bool = False, parking: bool = False) -> "EmployeeBuilder":
        self._data.update(has_laptop=laptop, has_parking=parking)
        return self

    def with_access(self, vpn: bool = False, admin: bool = False) -> "EmployeeBuilder":
        self._data.update(has_vpn_access=vpn, has_admin_rights=admin)
        return self

    def at_office(self, location: str) -> "EmployeeBuilder":
        self._data["office_location"] = location
        return self

    def with_contract(self, contract_type: str) -> "EmployeeBuilder":
        self._data["contract_type"] = contract_type
        return self

    def build(self) -> Employee:
        """All validation happens in one place, right before creating the product."""
        if not self._data.get("first_name") or not self._data.get("last_name"):
            raise ValueError("Name is required")
        if "@" not in (self._data.get("email") or ""):
            raise ValueError("Valid email is required")
        if not self._data.get("department") or not self._data.get("position"):
            raise ValueError("Job is required")
        if self._data["salary"] < 0:
            raise ValueError("Salary cannot be negative")
        return Employee(**self._data)


class DeveloperBuilder(EmployeeBuilder):
    """Preset: developers always get a laptop, VPN and admin rights."""

    def __init__(self, first_name: str, last_name: str, email: str, salary: float = 60000):
        super().__init__()
        (self.with_name(first_name, last_name)
             .with_email(email)
             .with_job("Engineering", "Developer", salary)
             .with_equipment(laptop=True)
             .with_access(vpn=True, admin=True)
             .at_office("Paris HQ"))


class InternBuilder(EmployeeBuilder):
    """Preset: interns get a laptop only and an internship contract."""

    def __init__(self, first_name: str, last_name: str, email: str, department: str):
        super().__init__()
        (self.with_name(first_name, last_name)
             .with_email(email)
             .with_job(department, "Intern", 15000)
             .with_equipment(laptop=True)
             .with_contract("internship")
             .at_office("Paris HQ"))


if __name__ == "__main__":
    employee = (
        EmployeeBuilder()
        .with_name("John", "Doe")
        .with_email("john.doe@company.com")
        .with_job("Engineering", "Senior Developer", 75000)
        .starting_on("2024-01-15")
        .with_equipment(laptop=True, parking=False)
        .with_access(vpn=True, admin=True)
        .build()
    )
    print(employee)

    dev = DeveloperBuilder("John", "Doe", "john.doe@company.com").build()
    intern = InternBuilder("Jane", "Smith", "jane.smith@company.com", "Marketing").with_manager(42).build()
    print(dev)
    print(intern)
