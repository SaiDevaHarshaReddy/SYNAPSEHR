"""HR Agent - Handles general HR queries and operations."""

from typing import Any

import structlog

from app.agents.base import BaseAgent

logger = structlog.get_logger()


class HRAgent(BaseAgent):
    """Agent for general HR operations."""

    def __init__(self):
        super().__init__(
            name="HR",
            description="Handles general HR queries, employee information, and policies",
        )

    async def process(self, input_data: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Process HR-related queries using the LLM and database context."""
        message = input_data.get("message", "")
        logger.info("hr_agent_processing", message=message[:100])

        db_context = context.get("db_context", {})
        
        from app.core.llm import generate_text
        import json
        
        system_prompt = (
            "You are the SynapseHR AI Assistant, a helpful and intelligent HR copilot. "
            "Your goal is to help the user with any HR queries or questions about the SynapseHR application.\n\n"
            "You have access to the following live database context:\n"
            f"- Current Logged-in User: {db_context.get('current_user_name')} (Role: {db_context.get('current_user_role')})\n"
            f"- Employees list in company:\n{json.dumps(db_context.get('employees'), indent=2)}\n\n"
            f"- Departments list in company:\n{json.dumps(db_context.get('departments'), indent=2)}\n\n"
            f"- Current User's Leave Balances:\n{json.dumps(db_context.get('my_leave_balances'), indent=2)}\n\n"
            f"- Current User's Leave Requests history:\n{json.dumps(db_context.get('my_leave_history'), indent=2)}\n\n"
            "Provide a helpful, accurate, direct, and natural response using the live data. "
            "Keep the response brief and professional. If the question is about policies and you don't know, suggest they check policy documents or knowledge base."
        )
        
        response_text = await generate_text(
            messages=[{"role": "user", "content": message}],
            system_prompt=system_prompt
        )
        
        if not response_text:
            # LLM unavailable - use database context to build a response
            response_text = self._fallback_response(message, db_context)

        # Classify action dynamically to maintain backward compatibility with tests/metrics
        action = "general_hr"
        message_lower = message.lower()
        if any(w in message_lower for w in ["headcount", "how many employees", "total employees"]):
            action = "headcount_query"
        elif any(w in message_lower for w in ["holiday", "holidays", "office closed"]):
            action = "holiday_query"
        elif any(w in message_lower for w in ["benefits", "insurance", "medical"]):
            action = "benefits_query"

        return {
            "action": action,
            "message": response_text,
        }

    def _fallback_response(self, message: str, db_context: dict) -> str:
        """Generate a fallback response using database context when LLM is unavailable."""
        msg = message.lower()
        employees = db_context.get("employees", [])
        departments = db_context.get("departments", [])
        balances = db_context.get("my_leave_balances", [])
        history = db_context.get("my_leave_history", [])
        user_name = db_context.get("current_user_name", "User")

        # Headcount queries
        if any(w in msg for w in ["headcount", "how many employees", "total employees", "employee count"]):
            active = [e for e in employees if e.get("status") == "active"]
            return f"Currently, there are **{len(active)}** active employees in the company (out of {len(employees)} total)."

        # Department queries
        if any(w in msg for w in ["department", "team", "division"]):
            if departments:
                dept_list = "\n".join(f"- **{d['name']}**: {d.get('description', 'No description')}" for d in departments)
                return f"We have **{len(departments)}** departments:\n\n{dept_list}"
            return "I don't have department information available right now."

        # Employee listing
        if any(w in msg for w in ["employee", "staff", "team member", "who works", "who are"]):
            if employees:
                emp_list = "\n".join(f"- **{e['name']}** ({e.get('designation', 'N/A')}) - {e.get('status', 'unknown')}" for e in employees[:15])
                suffix = f"\n...and {len(employees) - 15} more" if len(employees) > 15 else ""
                return f"Here are the employees I found:\n\n{emp_list}{suffix}"
            return "I don't have employee information available right now."

        # Leave balance
        if any(w in msg for w in ["balance", "leave balance", "remaining leave", "how many days"]):
            if balances:
                bal_list = "\n".join(f"- **{b['leave_type']}**: {b['available_days']} days available ({b['used_days']} used)" for b in balances)
                return f"Hi {user_name}, here are your leave balances:\n\n{bal_list}"
            return f"Hi {user_name}, I don't see any leave balances on record. You may need to have leave types set up first."

        # Leave history
        if any(w in msg for w in ["leave history", "past leave", "previous leave"]):
            if history:
                hist_list = "\n".join(f"- **{h['leave_type']}**: {h['start_date']} to {h['end_date']} ({h['status']})" for h in history[:10])
                return f"Here is your recent leave history:\n\n{hist_list}"
            return f"Hi {user_name}, you don't have any leave requests on record."

        # Benefits
        if any(w in msg for w in ["benefits", "insurance", "medical", "401k", "perks"]):
            return "SynapseHR offers a comprehensive benefits package including health insurance, dental coverage, vision care, and retirement plans. For detailed information about your specific benefits, please check the Knowledge Base or contact HR directly."

        # Holidays
        if any(w in msg for w in ["holiday", "holidays", "office closed"]):
            return "Please refer to the company holiday calendar in the Knowledge Base for the list of official holidays. You can also check with your manager for team-specific time off."

        # Greeting
        if any(w in msg for w in ["hello", "hi", "hey", "good morning", "good afternoon"]):
            return f"Hello {user_name}! I'm your AI HR assistant. I can help you with employee information, leave balances, department details, and general HR queries. How can I assist you today?"

        # Default
        return f"Hi {user_name}, I'm currently operating in offline mode (AI service unavailable). I can still help you with:\n\n- **Employee info**: Ask about employees or team members\n- **Departments**: Ask about company departments\n- **Leave balance**: Check your leave balances\n- **Leave history**: View your past leave requests\n- **Headcount**: Ask how many employees we have\n\nPlease try rephrasing your question, or check the Knowledge Base for policy information."
