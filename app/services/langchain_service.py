"""LangChain service for AI-powered content generation."""
import re
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from app.config import get_settings
from app.prompts import (
    BUSINESS_FLOW_SYSTEM_PROMPT,
    BUSINESS_FLOW_USER_PROMPT
)


class LangChainService:
    """Service for interacting with OpenAI via LangChain."""

    def __init__(self):
        """Initialize the LangChain service with OpenAI configuration."""
        settings = get_settings()
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.OPENAI_TEMPERATURE,
            max_tokens=settings.OPENAI_MAX_TOKENS,
            openai_api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_BASE,
        )

    async def generate_business_flow(
        self,
        requirements: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Generate business process flow diagram.

        Args:
            requirements: User requirements
            conversation_history: Optional conversation history

        Returns:
            Dictionary containing business flow data
        """
        # Build conversation context
        history_str = self._format_conversation_history(conversation_history or [])

        messages = [
            SystemMessage(content=BUSINESS_FLOW_SYSTEM_PROMPT),
            HumanMessage(content=BUSINESS_FLOW_USER_PROMPT.format(
                requirements=requirements,
                conversation_history=history_str
            ))
        ]

        response = await self.llm.ainvoke(messages)

        # Parse response into structured business flow
        business_flow = self._parse_business_flow(response.content)

        return {
            "business_flow": business_flow,
            "raw_response": response.content
        }

    def _format_conversation_history(self, history: List[Dict[str, str]]) -> str:
        """Format conversation history for prompt."""
        if not history:
            return "No previous conversation."

        formatted = []
        for msg in history[-5:]:  # Only include last 5 messages
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            formatted.append(f"{role.upper()}: {content}")

        return "\n".join(formatted)

    def _parse_business_flow(self, text: str) -> Dict[str, Any]:
        """Parse business flow response into structured data."""
        processes = []
        decisions = []

        # Extract processes
        process_pattern = r"PROCESS:\s*(\w+)(?:\s*\[actor=(\w+)\])?"
        for match in re.finditer(process_pattern, text, re.IGNORECASE):
            processes.append({
                "name": match.group(1),
                "actor": match.group(2) or "System"
            })

        # Extract decisions
        decision_pattern = r"DECISION:\s*(\w+)(?:\s*->\s*Yes:\s*(\w+),\s*No:\s*(\w+))?"
        for match in re.finditer(decision_pattern, text, re.IGNORECASE):
            decisions.append({
                "name": match.group(1),
                "true_branch": match.group(2),
                "false_branch": match.group(3)
            })

        # If no structured data, create generic flow
        if not processes:
            processes.append({"name": "Start Process", "actor": "User"})
            processes.append({"name": "Process Request", "actor": "System"})
            processes.append({"name": "Complete", "actor": "System"})

        return {"processes": processes, "decisions": decisions}
