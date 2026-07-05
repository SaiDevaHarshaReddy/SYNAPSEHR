"""Employee service."""

from typing import Optional
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateException, NotFoundException, ValidationException
from app.repositories.department import DepartmentRepository
from app.repositories.employee import EmployeeRepository
from app.schemas.common import PaginationParams
from app.schemas.employee import EmployeeCreate, EmployeeResponse, EmployeeUpdate

logger = structlog.get_logger()


class EmployeeService:
    """Handle employee business operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.employee_repo = EmployeeRepository(session)
        self.department_repo = DepartmentRepository(session)

    async def get_employee(self, employee_id: UUID) -> EmployeeResponse:
        """Get employee by ID."""
        employee = await self.employee_repo.get_with_department(employee_id)
        if employee is None:
            raise NotFoundException("Employee", str(employee_id))

        return EmployeeResponse(
            id=employee.id,
            user_id=employee.user_id,
            department_id=employee.department_id,
            employee_code=employee.employee_code,
            first_name=employee.first_name,
            last_name=employee.last_name,
            designation=employee.designation,
            phone=employee.phone,
            address=employee.address,
            gender=employee.gender,
            date_of_birth=employee.date_of_birth,
            joining_date=employee.joining_date,
            employment_type=employee.employment_type,
            status=employee.status,
            manager_id=employee.manager_id,
            created_at=employee.created_at,
            updated_at=employee.updated_at,
        )

    async def list_employees(
        self,
        pagination: PaginationParams,
        department_id: Optional[UUID] = None,
        status: Optional[str] = None,
    ) -> tuple[list[EmployeeResponse], int]:
        """List employees with pagination and filters."""
        filters = {}
        if department_id:
            filters["department_id"] = department_id
        if status:
            filters["status"] = status

        employees, total = await self.employee_repo.get_all(pagination, filters)

        responses = [
            EmployeeResponse(
                id=emp.id,
                user_id=emp.user_id,
                department_id=emp.department_id,
                employee_code=emp.employee_code,
                first_name=emp.first_name,
                last_name=emp.last_name,
                designation=emp.designation,
                phone=emp.phone,
                address=emp.address,
                gender=emp.gender,
                date_of_birth=emp.date_of_birth,
                joining_date=emp.joining_date,
                employment_type=emp.employment_type,
                status=emp.status,
                manager_id=emp.manager_id,
                created_at=emp.created_at,
                updated_at=emp.updated_at,
            )
            for emp in employees
        ]

        return responses, total

    async def create_employee(self, data: EmployeeCreate) -> EmployeeResponse:
        """Create a new employee."""
        # Check for duplicate employee code
        existing = await self.employee_repo.get_by_employee_code(data.employee_code)
        if existing:
            raise DuplicateException("Employee", f"Employee code '{data.employee_code}' already exists")

        # Validate department exists
        department = await self.department_repo.get_by_id(data.department_id)
        if department is None:
            raise NotFoundException("Department", str(data.department_id))

        employee = await self.employee_repo.create(
            user_id=data.user_id,
            department_id=data.department_id,
            employee_code=data.employee_code,
            first_name=data.first_name,
            last_name=data.last_name,
            designation=data.designation,
            phone=data.phone,
            address=data.address,
            gender=data.gender,
            date_of_birth=data.date_of_birth,
            joining_date=data.joining_date,
            employment_type=data.employment_type,
            status=data.status,
            manager_id=data.manager_id,
        )

        logger.info("employee_created", employee_id=str(employee.id))

        return EmployeeResponse(
            id=employee.id,
            user_id=employee.user_id,
            department_id=employee.department_id,
            employee_code=employee.employee_code,
            first_name=employee.first_name,
            last_name=employee.last_name,
            designation=employee.designation,
            phone=employee.phone,
            address=employee.address,
            gender=employee.gender,
            date_of_birth=employee.date_of_birth,
            joining_date=employee.joining_date,
            employment_type=employee.employment_type,
            status=employee.status,
            manager_id=employee.manager_id,
            created_at=employee.created_at,
            updated_at=employee.updated_at,
        )

    async def update_employee(
        self, employee_id: UUID, data: EmployeeUpdate
    ) -> EmployeeResponse:
        """Update an employee."""
        employee = await self.employee_repo.get_by_id(employee_id)
        if employee is None:
            raise NotFoundException("Employee", str(employee_id))

        update_data = data.model_dump(exclude_unset=True)
        updated = await self.employee_repo.update(employee_id, **update_data)

        logger.info("employee_updated", employee_id=str(employee_id))

        return EmployeeResponse(
            id=updated.id,
            user_id=updated.user_id,
            department_id=updated.department_id,
            employee_code=updated.employee_code,
            first_name=updated.first_name,
            last_name=updated.last_name,
            designation=updated.designation,
            phone=updated.phone,
            address=updated.address,
            gender=updated.gender,
            date_of_birth=updated.date_of_birth,
            joining_date=updated.joining_date,
            employment_type=updated.employment_type,
            status=updated.status,
            manager_id=updated.manager_id,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
        )

    async def deactivate_employee(self, employee_id: UUID) -> None:
        """Deactivate an employee."""
        employee = await self.employee_repo.get_by_id(employee_id)
        if employee is None:
            raise NotFoundException("Employee", str(employee_id))

        await self.employee_repo.update(employee_id, status="inactive")

        logger.info("employee_deactivated", employee_id=str(employee_id))
