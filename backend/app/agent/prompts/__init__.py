"""
Agent prompt templates.

Prompts are layered:
  Base System Prompt
    → Platform Rules
      → Business Context ({{business.name}}, {{business.type}})
        → Capability Instructions ({{capabilities}})
          → Current Workflow
"""
