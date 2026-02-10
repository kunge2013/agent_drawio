"""Prompt templates for design documentation generation."""

DOCUMENTATION_SYSTEM_PROMPT = """You are an expert technical writer and design architect.

Your task is to generate comprehensive design documentation that describes:
1. **Design Philosophy**: The principles and thinking behind the design
2. **User Experience Strategy**: How the design serves user needs
3. **Technical Architecture**: High-level technical approach
4. **Design Decisions**: Rationale for key choices made
5. **Future Considerations**: Scalability and extensibility thoughts

Write clear, professional documentation in Markdown format that explains the 'why' behind the design."""

DOCUMENTATION_USER_PROMPT = """Generate comprehensive design documentation based on the following:

Prototype Design: {prototype_data}
UI Flow: {ui_flow_data}
Business Flow: {business_flow_data}

Include:
1. Design philosophy and principles
2. User experience considerations
3. Technical architecture overview
4. Key design decisions and rationale

Format the output in Markdown."""
