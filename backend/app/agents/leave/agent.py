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

        # Determine specific leave action
        action = self._determine_action(message)

        result = {
            "action": action,
            "status": "processing",
        }

        if action == "check_balance":
            result["message"] = "I'll check your leave balance."
        elif action == "apply_leave":
            # 1. Fetch conversation history for date extraction context
            history_context = ""
            db = context.get("db")
            if db and conversation_id:
                from app.repositories.conversation import MessageRepository
                from uuid import UUID
                try:
                    msg_repo = MessageRepository(db)
                    history_msgs = await msg_repo.get_by_conversation(UUID(str(conversation_id)))
                    if history_msgs:
                        history_context = "\nConversation History:\n" + "\n".join(
                            f"{m.sender}: {m.message}" for m in history_msgs[-5:]
                        )
                except Exception as ex:
                    logger.error("leave_agent_history_failed", error=str(ex))

            # 2. Ask LLM to extract start_date, end_date, leave_type, and reason
            from app.core.llm import generate_text
            import json
            
            system_prompt = (
                "You are an HR extraction assistant. Extract leave request details from the user's message and history. "
                "Return ONLY a JSON object with the following keys, and nothing else (do not wrap in markdown ```json blocks, just return raw JSON):\n"
                "{\n"
                "  \"start_date\": \"YYYY-MM-DD\" or null,\n"
                "  \"end_date\": \"YYYY-MM-DD\" or null,\n"
                "  \"leave_type\": \"Casual Leave\" or \"Sick Leave\" or \"Annual Leave\" or null,\n"
                "  \"reason\": \"Reason text\" or null\n"
                "}\n"
                "Assume the current year is 2026 if relative dates like 'tomorrow', 'next week', or weekdays are used. Today is Sunday, July 5th, 2026."
            )
            
            user_prompt = f"User Message: {message}\n{history_context}"
            extracted_text = await generate_text(
                messages=[{"role": "user", "content": user_prompt}],
                system_prompt=system_prompt
            )
            
            start_date, end_date, leave_type, reason = None, None, None, None
            try:
                # Clean up any potential markdown formatting
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
                # Try regex-based date extraction as fallback
                import re
                date_pattern = r'(\d{4}-\d{2}-\d{2})'
                dates = re.findall(date_pattern, message)
                if len(dates) >= 2:
                    start_date = dates[0]
                    end_date = dates[1]
                    # Try to detect leave type from message
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
                else:
                    result["apply_now"] = False
                    result["message"] = (
                        "I'd be happy to help you apply for leave! Please specify the details:\n\n"
                        "- **Start date** (YYYY-MM-DD)\n"
                        "- **End date** (YYYY-MM-DD)\n"
                        "- **Leave type** (optional): Casual Leave, Sick Leave, Annual Leave, etc.\n"
                        "- **Reason** (optional)\n\n"
                        "For example: \"Apply for Casual Leave from 2026-07-10 to 2026-07-12 for a family event\""
                    )
        elif action == "cancel_leave":
            result["message"] = "I'll help you cancel your leave request."
        elif action == "view_history":
            result["message"] = "I'll retrieve your leave history."
        else:
            result["message"] = "I can help you with leave-related tasks. Would you like to check your balance, apply for leave, or view your leave history?"

        return result

    def _determine_action(self, message: str) -> str:
        """Determine the specific leave action."""
        message_lower = message.lower()

        if any(word in message_lower for word in ["balance", "remaining", "how many"]):
            return "check_balance"
        elif any(word in message_lower for word in ["apply", "request", "take leave", "take a leave", "want to take", "need to take", "pto", "vacation", "day off", "days off", "time off", "yes", "go ahead", "please do", "sure"]):
            return "apply_leave"
        elif any(word in message_lower for word in ["cancel", "withdraw"]):
            return "cancel_leave"
        elif any(word in message_lower for word in ["history", "past", "previous"]):
            return "view_history"
        else:
            return "info"
