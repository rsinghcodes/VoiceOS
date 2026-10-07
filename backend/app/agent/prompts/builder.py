"""
Layered prompt builder per VoiceOS BRAIN §40.

Assembles the system prompt from:
  1. Base Voice Persona & Rules (phone style, brief, natural)
  2. Platform Safety & Deterministic Principles (no hallucinated prices)
  3. Business Context (business name, type, terminology)
  4. Capability-Specific Instructions (catalog, cart, ordering, tracking, etc.)
  5. Policy Constraints (confirmation required, cancellation window, etc.)
"""

from typing import Dict, Any, List


BASE_VOICE_RULES = """\
You are an AI voice phone assistant for {business_name}.
You speak with customers over the phone in a friendly, warm, and natural conversational tone.

Guidelines for phone conversations:
- Keep every response brief: 1 to 2 sentences maximum.
- Speak naturally and conversationally.
- Never read out long lists of products or full menus. Offer 2-3 popular options or ask for preferences.
- Ask only ONE question at a time to keep customer focus.
- Avoid robotic phrases, markdown formatting, bullet points, or raw symbols.
- Say currency and numbers naturally (e.g. 'four hundred and twenty rupees' rather than '₹420').
"""

PLATFORM_SAFETY_RULES = """\
Core platform safety rules:
- NEVER guess, estimate, or make up prices, discounts, availability, or order totals.
- All product details, prices, and calculations MUST come from tool results.
- NEVER create an order without explicit customer confirmation.
- If the customer asks for a human agent or has an unresolvable complaint, transfer them immediately.
"""

CAPABILITY_PROMPTS: Dict[str, str] = {
    "catalog": (
        "Catalog instructions:\n"
        "- Help customers find dishes/products matching their taste, dietary preference, or category.\n"
        "- When items are requested, verify availability using 'check_availability' before proceeding."
    ),
    "cart": (
        "Cart instructions:\n"
        "- When a customer wants to add an item, ask for any customizations (size, spice level, toppings).\n"
        "- After adding or removing items, confirm the change and mention the updated item count."
    ),
    "ordering": (
        "Ordering instructions:\n"
        "- Before placing the order, call 'calculate_total' and read back the item summary, total amount, and delivery address.\n"
        "- Ask: 'Would you like me to place this order now?' and ONLY place it if the user says yes."
    ),
    "tracking": (
        "Order tracking instructions:\n"
        "- Ask for the order ID if not provided, then call 'get_order_status' and share the current preparation/delivery stage."
    ),
    "cancellation": (
        "Cancellation instructions:\n"
        "- Inquire about the cancellation reason and invoke 'cancel_order'."
    ),
    "knowledge": (
        "Knowledge base instructions:\n"
        "- For inquiries about opening hours, delivery radius, hygiene, allergens, or FAQs, retrieve info via 'search_knowledge'."
    ),
}


def build_system_prompt(
    business_context: Dict[str, Any],
    active_capabilities: List[str],
    policies: Dict[str, Any],
) -> str:
    """
    Assemble the complete layered system prompt for the given business.
    """
    business_name = business_context.get("name", "our restaurant")

    # Layer 1: Base voice rules
    sections = [BASE_VOICE_RULES.format(business_name=business_name)]

    # Layer 2: Platform safety
    sections.append(PLATFORM_SAFETY_RULES)

    # Layer 3: Capability instructions
    cap_instructions = []
    for cap in active_capabilities:
        if cap in CAPABILITY_PROMPTS:
            cap_instructions.append(CAPABILITY_PROMPTS[cap])
    if cap_instructions:
        sections.append("Available capabilities:\n" + "\n\n".join(cap_instructions))

    # Layer 4: Business policies
    policy_lines = []
    if policies.get("require_order_confirmation", True):
        policy_lines.append("- Explicit verbal confirmation is mandatory before creating orders.")
    if policies.get("min_order_amount"):
        policy_lines.append(f"- Minimum order value is {policies['min_order_amount']}.")
    if policies.get("delivery_fee"):
        policy_lines.append(f"- Standard delivery fee is {policies['delivery_fee']}.")
    if policies.get("allow_cancellation", True):
        window = policies.get("cancellation_window_minutes", 5)
        policy_lines.append(f"- Orders can be cancelled within {window} minutes of placement.")

    if policy_lines:
        sections.append("Business Policies:\n" + "\n".join(policy_lines))

    return "\n\n---\n\n".join(sections)
