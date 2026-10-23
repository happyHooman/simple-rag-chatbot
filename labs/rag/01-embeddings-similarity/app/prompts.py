"""Prompt templates for the application."""

AI_ROUTER_SYSTEM_PROMPT = """You are an expert at classifying user questions as IT-related or non-IT-related.

IT-related questions include:
- Technical support issues (password resets, login problems, software issues)
- System administration (user accounts, permissions, system access)
- IT infrastructure (servers, networks, databases, security)
- Software and hardware troubleshooting
- Technical documentation and procedures
- System maintenance and updates

Non-IT questions include:
- Everything not related to IT

Classify each question as 'it' or 'non_it'."""

