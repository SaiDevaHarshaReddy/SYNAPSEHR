"""Leave Agent - Handles leave operations."""

from typing import Any
from uuid import UUID

import structlog

from app.agents.base import BaseAgent

logger = structlog.get_logger()


class LeaveAgent(BaseAgent):
    """Agent that handles all leave-related operations."""

    def __init__(self):
        super().__init__(
            name="Leave",
            description="Handles leave requests, balances, and policies",
        )

    async def process(self, input_data: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Process leave-related requests."""
        message = input_data.get("message", "")
        user_id = context.get("user_id")
        conversation_id = input_data.get("conversation_id") or context.get("conversation_id")

        logger.info("leave_agent_processing", message=message[:100])

        action = self._determine_action(message)

        result = {
            "action": action,
            "status": "processing",
        }

        if action == "check_balance":
            db_context = context.get("db_context", {})
            balances = db_context.get("my_leave_balances", [])
            user_name = db_context.get("current_user_name", "User")
            
            if balances:
                bal_list = "\n".join(f"• **{b['leave_type']}**: {b['available_days']} days available ({b['used_days']} used)" for b in balances)
                result["message"] = (
                    f"Hi {user_name}! Here are your current leave balances:\n\n"
                    f"{bal_list}\n\n"
                    f"📝 Ready to apply? Just say: \"Apply for leave from YYYY-MM-DD to YYYY-MM-DD\""
                )
            else:
                result["message"] = (
                    f"Hi {user_name}, I don't see any leave balances on record. "
                    f"Please contact HR to get your leave types configured."
                )
            
        elif action == "apply_leave":
            history_context = ""
            db = context.get("db")
            if db and conversation_id:
                from app.repositories.conversation import MessageRepository
                try:
                    msg_repo = MessageRepository(db)
                    history_msgs = await msg_repo.get_by_conversation(UUID(str(conversation_id)))
                    if history_msgs:
                        history_context = "\nConversation History:\n" + "\n".join(
                            f"{m.sender}: {m.message}" for m in history_msgs[-5:]
                        )
                except Exception as ex:
                    logger.error("leave_agent_history_failed", error=str(ex))

            from app.core.llm import generate_text
            import json
            
            system_prompt = (
                "You are an HR extraction assistant. Extract leave request details from the user's message and history. "
                "Return ONLY a JSON object with the following keys, and nothing else (do not wrap in markdown ```json blocks, just return raw JSON):\n"
                "{\n"
                "  \"start_date\": \"YYYY-MM-DD\" or null,\n"
                "  \"end_date\": \"YYYY-MM-DD\" or null,\n"
                "  \"leave_type\": \"Casual Leave\" or \"Sick Leave\" or \"Annual Leave\" or \"Earned Leave\" or \"Maternity Leave\" or \"Paternity Leave\" or null,\n"
                "  \"reason\": \"Reason text\" or null\n"
                "}\n"
                "Assume the current year is 2026 if relative dates like 'tomorrow', 'next week', or weekdays are used. "
                "Today is Monday, July 6th, 2026.\n"
                "If the user provides only a start date, assume end date is the same day.\n"
                "If the user says 'tomorrow', calculate the actual date.\n"
                "If the user says 'next week', calculate the next Monday to Friday."
            )
            
            user_prompt = f"User Message: {message}\n{history_context}"
            extracted_text = await generate_text(
                messages=[{"role": "user", "content": user_prompt}],
                system_prompt=system_prompt
            )
            
            start_date, end_date, leave_type, reason = None, None, None, None
            try:
                clean_text = extracted_text.replace("```json", "").replace("```", "").strip()
                extracted_json = json.loads(clean_text)
                start_date = extracted_json.get("start_date")
                end_date = extracted_json.get("end_date")
                leave_type = extracted_json.get("leave_type")
                reason = extracted_json.get("reason")
            except Exception as e:
                logger.error("leave_agent_extraction_parse_failed", text=extracted_text, error=str(e))
                
            if start_date and end_date:
                result["apply_now"] = True
                result["start_date"] = start_date
                result["end_date"] = end_date
                result["leave_type"] = leave_type
                result["reason"] = reason or f"Applied via AI Assistant: {message}"
                result["message"] = f"Applying for {leave_type or 'leave'} from {start_date} to {end_date}..."
            else:
                import re
                date_pattern = r'(\d{4}-\d{2}-\d{2})'
                dates = re.findall(date_pattern, message)
                if len(dates) >= 2:
                    start_date = dates[0]
                    end_date = dates[1]
                    leave_type = None
                    for lt_name in ["Casual Leave", "Sick Leave", "Annual Leave", "Earned Leave", "Maternity Leave", "Paternity Leave"]:
                        if lt_name.lower().split()[0] in message.lower():
                            leave_type = lt_name
                            break
                    result["apply_now"] = True
                    result["start_date"] = start_date
                    result["end_date"] = end_date
                    result["leave_type"] = leave_type
                    result["reason"] = f"Applied via AI Assistant: {message}"
                    result["message"] = f"Applying for {leave_type or 'leave'} from {start_date} to {end_date}..."
                elif len(dates) == 1:
                    result["apply_now"] = True
                    result["start_date"] = dates[0]
                    result["end_date"] = dates[0]
                    leave_type = None
                    for lt_name in ["Casual Leave", "Sick Leave", "Annual Leave", "Earned Leave", "Maternity Leave", "Paternity Leave"]:
                        if lt_name.lower().split()[0] in message.lower():
                            leave_type = lt_name
                            break
                    result["leave_type"] = leave_type
                    result["reason"] = f"Applied via AI Assistant: {message}"
                    result["message"] = f"Applying for {leave_type or 'leave'} on {dates[0]}..."
                else:
                    result["apply_now"] = False
                    result["message"] = (
                        "I'd be happy to help you apply for leave! 📝\n\n"
                        "Please provide the details in any of these formats:\n\n"
                        "**Option 1:** \"Apply for Casual Leave from 2026-07-10 to 2026-07-12\"\n"
                        "**Option 2:** \"I need leave tomorrow\"\n"
                        "**Option 3:** \"Apply for leave from 2026-07-10 to 2026-07-12 for a family event\"\n\n"
                        "**Leave Types Available:**\n"
                        "• Casual Leave\n• Sick Leave\n• Annual Leave\n• Earned Leave\n• Maternity Leave\n• Paternity Leave\n\n"
                        "Just type your request and I'll take care of it!"
                    )

        elif action == "cancel_leave":
            db_context = context.get("db_context", {})
            user_name = db_context.get("current_user_name", "User")
            result["message"] = (
                f"I can help you cancel a leave request, {user_name}. "
                f"Please provide the leave request details or check your leave history first."
            )

        elif action == "view_history":
            db_context = context.get("db_context", {})
            history = db_context.get("my_leave_history", [])
            user_name = db_context.get("current_user_name", "User")
            
            if history:
                hist_list = "\n".join(f"• **{h['leave_type']}**: {h['start_date']} to {h['end_date']} ({h['status']})" for h in history[:10])
                result["message"] = (
                    f"Here's your recent leave history, {user_name}:\n\n"
                    f"{hist_list}\n\n"
                    f"Want to apply for new leave? Just say: \"Apply for leave from YYYY-MM-DD to YYYY-MM-DD\""
                )
            else:
                result["message"] = (
                    f"You don't have any leave requests on record yet, {user_name}. "
                    f"Ready to take some time off? Just say: \"Apply for leave from YYYY-MM-DD to YYYY-MM-DD\""
                )

        else:
            db_context = context.get("db_context", {})
            user_name = db_context.get("current_user_name", "User")
            balances = db_context.get("my_leave_balances", [])
            
            balance_info = ""
            if balances:
                bal_list = "\n".join(f"• **{b['leave_type']}**: {b['available_days']} days available" for b in balances)
                balance_info = f"\n\n📊 **Your Current Balances:**\n{bal_list}"
            
            result["message"] = (
                f"Hi {user_name}! I'm your leave assistant. Here's what I can help you with:\n\n"
                f"🏖️ **Apply for Leave**\n"
                f"   Say: \"Apply for leave from YYYY-MM-DD to YYYY-MM-DD\"\n\n"
                f"💰 **Check Balance**\n"
                f"   Say: \"Check my leave balance\"\n\n"
                f"📜 **View History**\n"
                f"   Say: \"Show my leave history\"\n\n"
                f"❌ **Cancel Leave**\n"
                f"   Say: \"Cancel my leave request\"\n"
                f"{balance_info}"
            )

        return result

    def _determine_action(self, message: str) -> str:
        """Determine the specific leave action."""
        message_lower = message.lower()

        if any(word in message_lower for word in ["balance", "remaining", "how many", "check balance", "leave balance"]):
            return "check_balance"
        elif any(word in message_lower for word in ["apply", "request", "take leave", "take a leave", "want to take", "need to take", "pto", "vacation", "day off", "days off", "time off", "yes", "go ahead", "please do", "sure", "from 20", "from tomorrow"]):
            return "apply_leave"
        elif any(word in message_lower for word in ["cancel", "withdraw"]):
            return "cancel_leave"
        elif any(word in message_lower for word in ["history", "past", "previous", "my leaves", "leave history"]):
            return "view_history"
        else:
            return "info"
