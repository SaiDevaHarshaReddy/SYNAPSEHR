"""Policy Agent - Handles knowledge retrieval via RAG."""

from typing import Any

import structlog

from app.agents.base import BaseAgent
from app.rag.retriever import Retriever

logger = structlog.get_logger()


class PolicyAgent(BaseAgent):
    """Agent that handles policy queries using RAG."""

    def __init__(self):
        super().__init__(
            name="Policy",
            description="Retrieves and explains company policies using RAG",
        )
        self.retriever = Retriever()

    async def process(self, input_data: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Process policy-related queries using RAG."""
        message = input_data.get("message", "")
        organization_id = context.get("organization_id")

        logger.info("policy_agent_processing", message=message[:100])

        try:
            # Retrieve relevant chunks from vector store
            results = await self.retriever.retrieve(
                query=message,
                organization_id=str(organization_id),
                n_results=5,
            )

            if not results:
                # Knowledge base empty - fall back to HR agent with database context
                logger.info("policy_agent_knowledge_empty", fallback_to_hr=True)
                return await self._fallback_to_hr(message, context)

            # Build context from retrieved chunks
            context_parts = []
            sources = []
            seen_sources = set()

            for result in results:
                source = result.get("source", "Unknown Document")
                content = result.get("content", "")
                score = result.get("relevance_score", 0)

                if score > 0.3:  # Minimum relevance threshold
                    context_parts.append(f"[Source: {source}]\n{content}")
                    if source not in seen_sources:
                        sources.append(source)
                        seen_sources.add(source)

            if not context_parts:
                return await self._fallback_to_hr(message, context)

            # Format response with source attribution
            policy_context = "\n\n---\n\n".join(context_parts)
            sources_text = ", ".join(sources) if sources else "company policies"

            # Use LLM to synthesize answer
            from app.core.llm import generate_text
            system_prompt = (
                "You are an HR Policy Assistant. Answer the user's query accurately using ONLY the provided policy context. "
                "Be professional, clear, and direct. If the context does not contain enough information to answer, state that clearly "
                "and advise the user to contact the HR department. Do not hallucinate or make up policies."
            )
            user_prompt = f"Policy Context:\n{policy_context}\n\nUser Question: {message}"
            
            synthesized_answer = await generate_text(
                messages=[{"role": "user", "content": user_prompt}],
                system_prompt=system_prompt
            )
            
            if synthesized_answer:
                response_message = f"{synthesized_answer}\n\n*Sources: {sources_text}*"
            else:
                response_message = (
                    f"Based on the {sources_text}, here is what I found:\n\n"
                    f"{policy_context}\n\n"
                    f"*Sources: {sources_text}*"
                )

            return {
                "action": "policy_search",
                "query": message,
                "status": "completed",
                "message": response_message,
                "sources": sources,
                "chunks_used": len(context_parts),
            }

        except Exception as e:
            logger.error("policy_agent_error", error=str(e))
            return await self._fallback_to_hr(message, context)

    async def _fallback_to_hr(self, message: str, context: dict) -> dict[str, Any]:
        """Fall back to HR agent response when knowledge base is empty."""
        from app.agents.hr.agent import HRAgent
        hr_agent = HRAgent()
        hr_result = await hr_agent.process({"message": message}, context)
        
        # Prepend a note about knowledge base
        hr_message = hr_result.get("message", "")
        fallback_note = (
            "*Note: The knowledge base is currently empty. "
            "For detailed policy information, please upload HR documents to the Knowledge Base, "
            "or contact your HR department.*\n\n"
        )
        
        return {
            "action": "policy_search",
            "query": message,
            "status": "fallback_to_hr",
            "message": fallback_note + hr_message,
            "sources": [],
        }
