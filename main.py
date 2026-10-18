from enum import Enum
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, field_validator

app = FastAPI(title="Employee API", version="1.0.0")


class Status(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class Employee(BaseModel):
    id: int
    name: str
    department: str
    status: Status


class EmployeeCreate(BaseModel):
    name: str
    department: str

    @field_validator("name", "department")
    @classmethod
    def not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("must not be empty")
        return v


class StatusUpdate(BaseModel):
    status: Status


# In-memory storage with sample data
employees: List[Employee] = [
    Employee(id=1, name="Rahul Sharma", department="Engineering", status=Status.ACTIVE),
    Employee(id=2, name="Priya Patel", department="HR", status=Status.ACTIVE),
    Employee(id=3, name="Amit Verma", department="Engineering", status=Status.INACTIVE),
]
next_id = 4


def find_employee(employee_id: int) -> Employee:
    for emp in employees:
        if emp.id == employee_id:
            return emp
    raise HTTPException(status_code=404, detail=f"Employee with id {employee_id} not found")


@app.get("/employees", response_model=List[Employee])
def get_employees(department: Optional[str] = Query(None, description="Filter by department")):
    if department:
        return [e for e in employees if e.department.lower() == department.strip().lower()]
    return employees


@app.get("/employees/{employee_id}", response_model=Employee)
def get_employee(employee_id: int):
    return find_employee(employee_id)


@app.post("/employees", response_model=Employee, status_code=201)
def create_employee(payload: EmployeeCreate):
    global next_id
    emp = Employee(id=next_id, name=payload.name, department=payload.department, status=Status.ACTIVE)
    next_id += 1
    employees.append(emp)
    return emp


@app.patch("/employees/{employee_id}/status", response_model=Employee)
def update_status(employee_id: int, payload: StatusUpdate):
    emp = find_employee(employee_id)
    emp.status = payload.status
    return emp
