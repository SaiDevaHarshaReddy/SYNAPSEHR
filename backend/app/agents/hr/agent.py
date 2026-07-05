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
            "You are SynapseHR AI, a friendly, intelligent, and helpful HR assistant chatbot. "
            "You are like a knowledgeable HR colleague who can answer any question about the workplace.\n\n"
            "Your personality:\n"
            "- Be warm, friendly, and conversational (like ChatGPT)\n"
            "- Use emojis occasionally to feel more human\n"
            "- Be concise but thorough\n"
            "- If you don't know something, say so honestly and suggest alternatives\n"
            "- You can help with: employee info, leave balances, applying for leave, department info, "
            "headcount, benefits, holidays, policies, and general HR questions\n\n"
            "You have access to live database context:\n"
            f"Current User: {db_context.get('current_user_name')} (Role: {db_context.get('current_user_role')})\n"
            f"Employees: {json.dumps(db_context.get('employees', []), indent=2)}\n"
            f"Departments: {json.dumps(db_context.get('departments', []), indent=2)}\n"
            f"Leave Balances: {json.dumps(db_context.get('my_leave_balances', []), indent=2)}\n"
            f"Leave History: {json.dumps(db_context.get('my_leave_history', []), indent=2)}\n\n"
            "Instructions:\n"
            "- Answer based on the live data above\n"
            "- For leave requests, tell the user they can say 'Apply for leave from YYYY-MM-DD to YYYY-MM-DD'\n"
            "- For greetings, be warm and mention what you can help with\n"
            "- Use markdown formatting for readability (bold, lists)\n"
            "- Keep responses natural and conversational, not robotic\n"
        )
        
        response_text = await generate_text(
            messages=[{"role": "user", "content": message}],
            system_prompt=system_prompt
        )
        
        if not response_text:
            response_text = self._fallback_response(message, db_context)

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
        """Generate a conversational fallback response using database context when LLM is unavailable."""
        msg = message.lower()
        employees = db_context.get("employees", [])
        departments = db_context.get("departments", [])
        balances = db_context.get("my_leave_balances", [])
        history = db_context.get("my_leave_history", [])
        user_name = db_context.get("current_user_name", "User")

        # Greetings
        if any(w in msg for w in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]):
            return (
                f"Hey {user_name}! 👋 Welcome back!\n\n"
                f"I'm your AI HR assistant, and I'm here to help with anything HR-related. Here's what I can do:\n\n"
                f"📋 **Employee Info** - Ask about colleagues or team members\n"
                f"🏖️ **Leave Management** - Check balances, apply for leave, view history\n"
                f"🏢 **Departments** - Explore company departments\n"
                f"📊 **Headcount** - See how many people work here\n"
                f"🎁 **Benefits** - Learn about your benefits package\n"
                f"📅 **Holidays** - Check company holidays\n\n"
                f"What would you like to know?"
            )

        # Headcount queries
        if any(w in msg for w in ["headcount", "how many employees", "total employees", "employee count"]):
            active = [e for e in employees if e.get("status") == "active"]
            return (
                f"Here's the current headcount for you, {user_name}:\n\n"
                f"👥 **Active Employees:** {len(active)}\n"
                f"📋 **Total Employees:** {len(employees)}\n\n"
                f"Need details about a specific department or team? Just ask!"
            )

        # Department queries
        if any(w in msg for w in ["department", "team", "division"]):
            if departments:
                dept_list = "\n".join(f"• **{d['name']}** - {d.get('description', 'No description')}" for d in departments)
                return (
                    f"We have **{len(departments)}** departments in the company:\n\n"
                    f"{dept_list}\n\n"
                    f"Want to know who's in a specific department? Just ask!"
                )
            return "I don't have department information available right now. Please check back later or contact HR."

        # Employee listing
        if any(w in msg for w in ["employee", "staff", "team member", "who works", "who are"]):
            if employees:
                emp_list = "\n".join(f"• **{e['name']}** - {e.get('designation', 'N/A')} ({e.get('status', 'unknown')})" for e in employees[:15])
                suffix = f"\n\n...and **{len(employees) - 15}** more employees" if len(employees) > 15 else ""
                return (
                    f"Here are the employees I found:\n\n"
                    f"{emp_list}{suffix}\n\n"
                    f"Want to know more about a specific person? Just ask!"
                )
            return "I don't have employee information available right now. Please try again later."

        # Leave balance
        if any(w in msg for w in ["balance", "leave balance", "remaining leave", "how many days", "leave days"]):
            if balances:
                bal_list = "\n".join(f"• **{b['leave_type']}**: {b['available_days']} days available ({b['used_days']} used)" for b in balances)
                return (
                    f"Hi {user_name}! Here are your current leave balances:\n\n"
                    f"{bal_list}\n\n"
                    f"📝 **To apply for leave**, just say: \"Apply for leave from YYYY-MM-DD to YYYY-MM-DD\"\n"
                    f"📅 **To view history**, say: \"Show my leave history\""
                )
            return (
                f"Hi {user_name}, I don't see any leave balances on record yet. "
                f"This might be because leave types haven't been set up. "
                f"Please contact your HR department to get this configured."
            )

        # Leave history
        if any(w in msg for w in ["leave history", "past leave", "previous leave", "my leaves"]):
            if history:
                hist_list = "\n".join(f"• **{h['leave_type']}**: {h['start_date']} to {h['end_date']} ({h['status']})" for h in history[:10])
                return (
                    f"Here's your recent leave history, {user_name}:\n\n"
                    f"{hist_list}\n\n"
                    f"Want to apply for new leave? Just say: \"Apply for leave from YYYY-MM-DD to YYYY-MM-DD\""
                )
            return (
                f"Hi {user_name}, you don't have any leave requests on record yet. "
                f"Ready to take some time off? Just say: \"Apply for leave from YYYY-MM-DD to YYYY-MM-DD\""
            )

        # Apply leave hint
        if any(w in msg for w in ["apply", "request leave", "take leave", "want leave", "need leave"]):
            return (
                f"Great, {user_name}! I can help you apply for leave. 📝\n\n"
                f"Just tell me the details in this format:\n"
                f"\"Apply for leave from **YYYY-MM-DD** to **YYYY-MM-DD**\"\n\n"
                f"You can also specify:\n"
                f"• **Leave type**: Casual, Sick, Annual, etc.\n"
                f"• **Reason**: Your reason for leave\n\n"
                f"Example: \"Apply for Casual Leave from 2026-07-10 to 2026-07-12 for a family event\""
            )

        # Benefits
        if any(w in msg for w in ["benefits", "insurance", "medical", "401k", "perks", "health"]):
            return (
                f"Here's an overview of the benefits at SynapseHR, {user_name}:\n\n"
                f"🏥 **Health Insurance** - Comprehensive medical coverage\n"
                f"🦷 **Dental Coverage** - Dental care benefits\n"
                f"👓 **Vision Care** - Eye care benefits\n"
                f"💰 **Retirement Plans** - 401(k) and pension options\n"
                f"🎯 **Other Perks** - Wellness programs, employee discounts, and more\n\n"
                f"For detailed information about your specific benefits, please check the Knowledge Base or contact HR directly."
            )

        # Holidays
        if any(w in msg for w in ["holiday", "holidays", "office closed", "time off"]):
            return (
                f"📅 **Company Holidays**\n\n"
                f"Please refer to the company holiday calendar in the Knowledge Base for the complete list of official holidays.\n\n"
                f"You can also check with your manager for team-specific time off. "
                f"Need to request time off? Just say: \"Apply for leave from YYYY-MM-DD to YYYY-MM-DD\""
            )

        # Policy related
        if any(w in msg for w in ["policy", "policies", "rule", "rules", "guideline", "handbook"]):
            return (
                f"I can help with policy questions, {user_name}! 📚\n\n"
                f"For detailed policy information, please check the **Knowledge Base** or **Policies** section in the sidebar.\n\n"
                f"If you have a specific policy question, feel free to ask and I'll do my best to help!"
            )

        # Documents
        if any(w in msg for w in ["document", "letter", "certificate", "generate"]):
            return (
                f"I can help you generate HR documents, {user_name}! 📄\n\n"
                f"Just tell me what you need:\n"
                f"• Experience letter\n"
                f"• Salary certificate\n"
                f"• Offer letter\n"
                f"• Any other HR document\n\n"
                f"What would you like me to generate?"
            )

        # Thanks
        if any(w in msg for w in ["thank", "thanks", "appreciate"]):
            return f"You're welcome, {user_name}! 😊 Is there anything else I can help you with?"

        # How are you / status
        if any(w in msg for w in ["how are you", "what's up", "how's it going", "status"]):
            return (
                f"I'm doing great, thanks for asking! 😊\n\n"
                f"I'm here and ready to help with any HR tasks. "
                f"What can I do for you today?"
            )

        # Help
        if any(w in msg for w in ["help", "what can you do", "capabilities", "features"]):
            return (
                f"Here's everything I can help you with, {user_name}:\n\n"
                f"📋 **Employee Management**\n"
                f"   • View employee list and details\n"
                f"   • Check headcount\n\n"
                f"🏖️ **Leave Management**\n"
                f"   • Check leave balances\n"
                f"   • Apply for leave\n"
                f"   • View leave history\n\n"
                f"🏢 **Department Info**\n"
                f"   • View departments\n"
                f"   • See team structures\n\n"
                f"📄 **Documents**\n"
                f"   • Generate experience letters\n"
                f"   • Create salary certificates\n\n"
                f"📊 **Analytics**\n"
                f"   • View HR reports\n"
                f"   • Check trends\n\n"
                f"Just type your question or request, and I'll take care of it!"
            )

        # Default - comprehensive fallback
        return (
            f"Thanks for your message, {user_name}! I'm here to help. 😊\n\n"
            f"Here are some things you can try:\n\n"
            f"• **\"Show my leave balance\"** - Check your available leaves\n"
            f"• **\"Apply for leave from 2026-07-10 to 2026-07-12\"** - Apply for leave\n"
            f"• **\"Who are the employees?\"** - View team members\n"
            f"• **\"Show departments\"** - View company departments\n"
            f"• **\"How many employees?\"** - Check headcount\n"
            f"• **\"What are the holidays?\"** - View holiday calendar\n"
            f"• **\"Help\"** - See all available features\n\n"
            f"Feel free to ask me anything HR-related!"
        )
