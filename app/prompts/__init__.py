"""Prompt templates for LLM-based generation."""
from app.prompts.prototype_prompt import (
    PROTOTYPE_SYSTEM_PROMPT,
    PROTOTYPE_USER_PROMPT
)
from app.prompts.ui_flow_prompt import (
    UI_FLOW_SYSTEM_PROMPT,
    UI_FLOW_USER_PROMPT
)
from app.prompts.business_flow_prompt import (
    BUSINESS_FLOW_SYSTEM_PROMPT,
    BUSINESS_FLOW_USER_PROMPT
)
from app.prompts.documentation_prompt import (
    DOCUMENTATION_SYSTEM_PROMPT,
    DOCUMENTATION_USER_PROMPT
)

__all__ = [
    "PROTOTYPE_SYSTEM_PROMPT",
    "PROTOTYPE_USER_PROMPT",
    "UI_FLOW_SYSTEM_PROMPT",
    "UI_FLOW_USER_PROMPT",
    "BUSINESS_FLOW_SYSTEM_PROMPT",
    "BUSINESS_FLOW_USER_PROMPT",
    "DOCUMENTATION_SYSTEM_PROMPT",
    "DOCUMENTATION_USER_PROMPT",
]
