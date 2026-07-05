"""Chat API routes with AI integration and conversation persistence."""

import time
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database.database import get_db
from app.repositories.conversation import ConversationRepository, MessageRepository
from app.repositories.employee import EmployeeRepository
from app.schemas.chat import ChatRequest, ChatResponse, ConversationDetail, ConversationResponse, MessageResponse
from app.schemas.response import SuccessResponse

router = APIRouter(prefix="/chat", tags=["AI Chat"])


@router.post("", response_model=SuccessResponse[ChatResponse])
async def chat(
    data: ChatRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a message to the AI assistant."""
    start_time = time.time()

    # Get employee
    emp_repo = EmployeeRepository(db)
    employee = await emp_repo.get_by_user_id(UUID(current_user["user_id"]))

    if employee is None:
        from sqlalchemy import select
        from app.models.department import Department
        import uuid
        from app.models.employee import Employee
        from app.models.user import User
        import random

        org_id = UUID(current_user["organization_id"])
        
        # Find department in this organization
        dept_result = await db.execute(
            select(Department).where(Department.organization_id == org_id)
        )
        department = dept_result.scalars().first()
        if not department:
            department = Department(
                id=uuid.uuid4(),
                organization_id=org_id,
                name="Operations",
                description="Default Operations Department",
            )
            db.add(department)
            await db.flush()

        # Get user email
        user_result = await db.execute(select(User).where(User.id == UUID(current_user["user_id"])))
        user_obj = user_result.scalar_one_or_none()
        email = user_obj.email if user_obj else "admin@synapsehr.com"
        username = email.split("@")[0]
        first_name = username.capitalize()
        last_name = "User"

        # Create employee profile
        emp_code = f"EMP{random.randint(1000, 9999)}"
        while True:
            existing = await emp_repo.get_by_employee_code(emp_code)
            if not existing:
                break
            emp_code = f"EMP{random.randint(1000, 9999)}"

        employee = Employee(
            id=uuid.uuid4(),
            user_id=UUID(current_user["user_id"]),
            department_id=department.id,
            employee_code=emp_code,
            first_name=first_name,
            last_name=last_name,
            designation=f"{current_user['role'].capitalize()} Profile",
            joining_date=datetime.now().date(),
            employment_type="full_time",
            status="active",
        )
        db.add(employee)
        await db.commit()
        
        # Reload employee
        employee = await emp_repo.get_by_user_id(UUID(current_user["user_id"]))

    # Fetch live database context for the AI Assistant
    from sqlalchemy import select
    from app.models.employee import Employee
    from app.models.department import Department
    from app.models.leave_balance import LeaveBalance
    from app.models.leave_type import LeaveType
    from app.models.leave_request import LeaveRequest
    
    employees_data = []
    try:
        emp_result = await db.execute(select(Employee))
        all_employees = emp_result.scalars().all()
        employees_data = [
            {
                "name": f"{e.first_name} {e.last_name}",
                "code": e.employee_code,
                "designation": e.designation,
                "status": e.status,
                "employment_type": e.employment_type,
            }
            for e in all_employees
        ]
    except Exception:
        pass
    
    departments_data = []
    try:
        dept_result = await db.execute(select(Department))
        all_departments = dept_result.scalars().all()
        departments_data = [
            {
                "name": d.name,
                "description": d.description,
            }
            for d in all_departments
        ]
    except Exception:
        pass
    
    balances_data = []
    try:
        balance_result = await db.execute(
            select(LeaveBalance, LeaveType)
            .join(LeaveType, LeaveBalance.leave_type_id == LeaveType.id)
            .where(LeaveBalance.employee_id == employee.id)
        )
        for bal, lt in balance_result.all():
            balances_data.append({
                "leave_type": lt.name,
                "available_days": bal.available_days,
                "used_days": bal.used_days,
            })
    except Exception:
        pass
        
    history_data = []
    try:
        history_result = await db.execute(
            select(LeaveRequest, LeaveType)
            .join(LeaveType, LeaveRequest.leave_type_id == LeaveType.id)
            .where(LeaveRequest.employee_id == employee.id)
            .order_by(LeaveRequest.created_at.desc())
        )
        for req, lt in history_result.all():
            history_data.append({
                "leave_type": lt.name,
                "start_date": str(req.start_date),
                "end_date": str(req.end_date),
                "status": req.status.value if hasattr(req.status, 'value') else str(req.status),
                "reason": req.reason,
            })
    except Exception:
        pass

    db_context = {
        "current_user_name": f"{employee.first_name} {employee.last_name}",
        "current_user_role": current_user["role"],
        "employees": employees_data,
        "departments": departments_data,
        "my_leave_balances": balances_data,
        "my_leave_history": history_data,
    }

    # Create context
    context = {
        "user_id": current_user["user_id"],
        "organization_id": current_user["organization_id"],
        "role": current_user["role"],
        "employee_id": str(employee.id),
        "db": db,
        "db_context": db_context,
    }

    # Use planner agent with all specialized agents
    from app.agents.planner.agent import PlannerAgent
    from app.agents.leave.agent import LeaveAgent
    from app.agents.policy.agent import PolicyAgent
    from app.agents.document.agent import DocumentAgent
    from app.agents.hr.agent import HRAgent
    from app.agents.approval.agent import ApprovalAgent
    from app.agents.analytics.agent import AnalyticsAgent

    planner = PlannerAgent()
    planner.register_agent("leave", LeaveAgent())
    planner.register_agent("policy", PolicyAgent())
    planner.register_agent("document", DocumentAgent())
    planner.register_agent("hr", HRAgent())
    planner.register_agent("approval", ApprovalAgent())
    planner.register_agent("analytics", AnalyticsAgent())

    input_data = {"message": data.message, "conversation_id": str(data.conversation_id) if data.conversation_id else None}

    try:
        result = await planner.process(input_data, context)

        # Extract response
        intent = result.get("intent", "general_inquiry")
        agent_result = result.get("agent_result", {})

        response_text = agent_result.get("message", "I'm processing your request.")
        sources_used = agent_result.get("sources", None)

        # Execute workflow if needed
        workflow_steps = None
        if intent == "leave_request" and agent_result.get("apply_now") is True:
            from app.workflows.engine import workflow_engine, initialize_workflows
            initialize_workflows()
            
            start_date = agent_result.get("start_date")
            end_date = agent_result.get("end_date")
            leave_type = agent_result.get("leave_type")
            reason = agent_result.get("reason", data.message)
            
            # Resolve leave_type_id from DB
            from sqlalchemy import select
            from app.models.leave_type import LeaveType
            
            leave_types_result = await db.execute(
                select(LeaveType).where(LeaveType.organization_id == UUID(current_user["organization_id"]))
            )
            leave_types = leave_types_result.scalars().all()
            
            leave_type_id = ""
            matched_type_name = "Leave"
            if leave_types:
                leave_type_id = str(leave_types[0].id)
                matched_type_name = leave_types[0].name
                for lt in leave_types:
                    if leave_type and leave_type.lower() in lt.name.lower():
                        leave_type_id = str(lt.id)
                        matched_type_name = lt.name
                        break
            
            workflow = workflow_engine.create_workflow(
                "leave_request",
                employee_id=str(employee.id),
                leave_type_id=leave_type_id,
                start_date=start_date,
                end_date=end_date,
                reason=reason,
            )
            workflow_result = await workflow_engine.execute_workflow(workflow, context)
            
            if workflow_result.get("status") == "completed":
                response_text = f"**Intent:** Leave Request\n\nI have successfully applied for {matched_type_name} for you from {start_date} to {end_date}."
            elif workflow_result.get("status") == "waiting_approval":
                response_text = f"**Intent:** Leave Request\n\nYour leave request for {matched_type_name} from {start_date} to {end_date} has been submitted and is waiting for approval."
            else:
                error_msg = workflow_result.get("error", "Unknown error")
                response_text = f"**Intent:** Leave Request\n\nI tried to apply for leave but encountered an error: {error_msg}."
                
            workflow_steps = [{"step": k, "result": v} for k, v in workflow_result.get("state", {}).items()]

        execution_time = int((time.time() - start_time) * 1000)

        # --- Conversation Persistence ---
        conv_repo = ConversationRepository(db)
        msg_repo = MessageRepository(db)

        conversation_id = data.conversation_id
        if conversation_id is None:
            # Create new conversation
            title = data.message[:80] + ("..." if len(data.message) > 80 else "")
            conversation = await conv_repo.create(
                employee_id=employee.id,
                title=title,
                started_at=datetime.now(timezone.utc),
            )
            await db.commit()
            conversation_id = conversation.id
        else:
            # Verify conversation exists
            conversation = await conv_repo.get_by_id(conversation_id)
            if conversation is None:
                from app.core.exceptions import NotFoundException
                raise NotFoundException("Conversation", str(conversation_id))

        # Save user message
        await msg_repo.create(
            conversation_id=conversation_id,
            sender="user",
            message=data.message,
        )

        # Save assistant message
        await msg_repo.create(
            conversation_id=conversation_id,
            sender="assistant",
            message=response_text,
            token_usage=execution_time,  # approximate
        )

        await db.commit()

        return SuccessResponse(
            message="Message processed",
            data=ChatResponse(
                response=response_text,
                conversation_id=conversation_id,
                workflow_steps=workflow_steps,
                sources_used=sources_used,
                execution_time_ms=execution_time,
            ),
        )

    except Exception as e:
        execution_time = int((time.time() - start_time) * 1000)
        return SuccessResponse(
            message="Message processed",
            data=ChatResponse(
                response=f"I encountered an error processing your request: {str(e)}. Please try again or contact support.",
                conversation_id=data.conversation_id or UUID("00000000-0000-0000-0000-000000000000"),
                workflow_steps=None,
                sources_used=None,
                execution_time_ms=execution_time,
            ),
        )


@router.get("/history", response_model=SuccessResponse[list[ConversationResponse]])
async def get_chat_history(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get conversation history."""
    from app.repositories.conversation import ConversationRepository

    emp_repo = EmployeeRepository(db)
    employee = await emp_repo.get_by_user_id(UUID(current_user["user_id"]))

    if employee is None:
        return SuccessResponse(message="No conversations found", data=[])

    conv_repo = ConversationRepository(db)
    conversations = await conv_repo.get_by_employee(employee.id)

    return SuccessResponse(
        message="Chat history retrieved",
        data=[
            ConversationResponse(
                id=c.id,
                employee_id=c.employee_id,
                title=c.title,
                started_at=c.started_at,
                ended_at=c.ended_at,
                created_at=c.created_at,
            )
            for c in conversations
        ],
    )


@router.get("/{conversation_id}", response_model=SuccessResponse[ConversationDetail])
async def get_conversation(
    conversation_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get conversation with messages."""
    from app.repositories.conversation import ConversationRepository

    conv_repo = ConversationRepository(db)
    conversation = await conv_repo.get_with_messages(conversation_id)

    if conversation is None:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Conversation", str(conversation_id))

    return SuccessResponse(
        message="Conversation retrieved",
        data=ConversationDetail(
            id=conversation.id,
            employee_id=conversation.employee_id,
            title=conversation.title,
            started_at=conversation.started_at,
            ended_at=conversation.ended_at,
            messages=[
                MessageResponse(
                    id=m.id,
                    conversation_id=m.conversation_id,
                    sender=m.sender,
                    message=m.message,
                    token_usage=m.token_usage,
                    created_at=m.created_at,
                )
                for m in conversation.messages
            ],
            created_at=conversation.created_at,
        ),
    )
