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
            return "无历史对话"

        formatted = []
        for msg in history[-5:]:  # Only include last 5 messages
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            role_zh = "用户" if role == "user" else "助手"
            formatted.append(f"{role_zh}: {content}")

        return "\n".join(formatted)

    def _parse_business_flow(self, text: str) -> Dict[str, Any]:
        """Parse business flow response into structured data."""
        processes = []
        decisions = []

        # Extract processes - 支持中文字符
        process_pattern = r"PROCESS:\s*([^\[\n]+?)(?:\s*\[actor=([^\[\]]+)\])?"
        for match in re.finditer(process_pattern, text, re.IGNORECASE):
            name = match.group(1).strip()
            actor = match.group(2).strip() if match.group(2) else "系统"
            if name and not name.startswith("DECISION"):
                processes.append({
                    "name": name,
                    "actor": actor
                })

        # Extract decisions - 支持中文 "是/否" 和英文 "Yes/No"
        # 格式: DECISION: 决策名称 -> 是:步骤A, 否:步骤B 或 DECISION: 决策名称 -> Yes:StepA, No:StepB
        decision_pattern = r"DECISION:\s*([^\[->\n]+?)\s*(?:->\s*(?:是|Yes):\s*([^\n,]+?)(?:\s*,\s*(?:否|No):\s*([^\n]+?))?)?"
        for match in re.finditer(decision_pattern, text, re.IGNORECASE):
            name = match.group(1).strip() if match.group(1) else ""
            true_branch = match.group(2).strip() if match.group(2) else None
            false_branch = match.group(3).strip() if match.group(3) else None

            if name:
                decisions.append({
                    "name": name,
                    "true_branch": true_branch,
                    "false_branch": false_branch
                })

        # If no structured data, create generic flow (中文)
        if not processes:
            processes.append({"name": "开始", "actor": "用户"})
            processes.append({"name": "处理请求", "actor": "系统"})
            processes.append({"name": "完成", "actor": "系统"})

        return {"processes": processes, "decisions": decisions}
