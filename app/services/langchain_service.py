"""LangChain service for AI-powered content generation."""
import re
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from app.config import get_settings
from app.prompts import (
    PROTOTYPE_SYSTEM_PROMPT,
    PROTOTYPE_USER_PROMPT,
    UI_FLOW_SYSTEM_PROMPT,
    UI_FLOW_USER_PROMPT,
    BUSINESS_FLOW_SYSTEM_PROMPT,
    BUSINESS_FLOW_USER_PROMPT,
    DOCUMENTATION_SYSTEM_PROMPT,
    DOCUMENTATION_USER_PROMPT
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
            base_url = settings.OPENAI_API_BASE,
        )

    async def generate_prototype(
        self,
        user_requirements: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Generate prototype design based on user requirements.

        Args:
            user_requirements: User's product requirements
            conversation_history: Optional conversation history

        Returns:
            Dictionary containing prototype design data
        """
        # Build conversation context
        history_str = self._format_conversation_history(conversation_history or [])

        # Create messages
        messages = [
            SystemMessage(content=PROTOTYPE_SYSTEM_PROMPT),
            HumanMessage(content=PROTOTYPE_USER_PROMPT.format(
                requirements=user_requirements,
                conversation_history=history_str
            ))
        ]

        # Get response from LLM
        response = await self.llm.ainvoke(messages)

        # Parse response into structured data
        prototype_data = self._parse_prototype_response(response.content)

        return {
            "prototype_description": response.content,
            "screens": prototype_data.get("screens", []),
            "components": prototype_data.get("components", [])
        }

    async def generate_ui_flow(
        self,
        prototype_data: Dict[str, Any],
        requirements: str
    ) -> Dict[str, Any]:
        """
        Generate UI flow diagram data.

        Args:
            prototype_data: Previously generated prototype data
            requirements: Original user requirements

        Returns:
            Dictionary containing UI flow data with nodes and edges
        """
        prototype_description = prototype_data.get("prototype_description", "")

        messages = [
            SystemMessage(content=UI_FLOW_SYSTEM_PROMPT),
            HumanMessage(content=UI_FLOW_USER_PROMPT.format(
                requirements=requirements,
                prototype_data=prototype_description
            ))
        ]

        response = await self.llm.ainvoke(messages)

        # Parse response into structured flow data
        flow_data = self._parse_flow_response(response.content)

        return {
            "flow_data": flow_data,
            "raw_response": response.content
        }

    async def generate_business_flow(
        self,
        requirements: str,
        prototype_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate business process flow diagram.

        Args:
            requirements: User requirements
            prototype_data: Prototype design context

        Returns:
            Dictionary containing business flow data
        """
        prototype_description = prototype_data.get("prototype_description", "")

        messages = [
            SystemMessage(content=BUSINESS_FLOW_SYSTEM_PROMPT),
            HumanMessage(content=BUSINESS_FLOW_USER_PROMPT.format(
                requirements=requirements,
                prototype_data=prototype_description
            ))
        ]

        response = await self.llm.ainvoke(messages)

        # Parse response into structured business flow
        business_flow = self._parse_business_flow(response.content)

        return {
            "business_flow": business_flow,
            "raw_response": response.content
        }

    async def generate_documentation(
        self,
        all_data: Dict[str, Any]
    ) -> str:
        """
        Generate design documentation describing design philosophy.

        Args:
            all_data: Dictionary containing all generated data

        Returns:
            Markdown documentation string
        """
        messages = [
            SystemMessage(content=DOCUMENTATION_SYSTEM_PROMPT),
            HumanMessage(content=DOCUMENTATION_USER_PROMPT.format(
                prototype_data=all_data.get("prototype", {}),
                ui_flow_data=all_data.get("ui_flow", {}),
                business_flow_data=all_data.get("business_flow", {})
            ))
        ]

        response = await self.llm.ainvoke(messages)

        return response.content

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

    def _parse_prototype_response(self, text: str) -> Dict[str, Any]:
        """Parse prototype response into structured data."""
        screens = []
        components = []

        # Extract screens
        screen_pattern = r"SCREEN:\s*(.+?)(?:\n|$)"
        for match in re.finditer(screen_pattern, text, re.IGNORECASE):
            screens.append({"name": match.group(1).strip()})

        # Extract components
        component_pattern = r"Components?:\s*(.+?)(?:\n|$)"
        for match in re.finditer(component_pattern, text, re.IGNORECASE):
            components_text = match.group(1)
            # Split by common separators
            for comp in re.split(r"[,;·]", components_text):
                comp = comp.strip()
                if comp:
                    components.append({"type": comp})

        return {
            "screens": screens,
            "components": components
        }

    def _parse_flow_response(self, text: str) -> Dict[str, Any]:
        """Parse flow response into nodes and edges."""
        nodes = []
        edges = []

        # Extract nodes
        node_pattern = r"NODE:\s*(\w+)\s*\[type=(\w+)\]"
        for match in re.finditer(node_pattern, text, re.IGNORECASE):
            nodes.append({
                "name": match.group(1),
                "type": match.group(2).lower()
            })

        # Extract edges
        edge_pattern = r"EDGE:\s*(\w+)\s*->\s*(\w+)(?:\s*\[label=\"([^\"]+)\"\])?"
        for match in re.finditer(edge_pattern, text, re.IGNORECASE):
            edges.append({
                "from": match.group(1),
                "to": match.group(2),
                "label": match.group(3) or ""
            })

        # If no structured data found, create from screen mentions
        if not nodes:
            screen_mentions = re.findall(r"\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)\b", text)
            for idx, screen in enumerate(list(set(screen_mentions))[:10]):
                nodes.append({"name": screen, "type": "screen"})
                if idx > 0:
                    edges.append({"from": screen_mentions[idx-1], "to": screen, "label": ""})

        return {"nodes": nodes, "edges": edges}

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
