BLOCKED_KEYWORDS = [
    "password", "credit card", "ssn", "social security",
    "hack", "exploit", "malware"
]


def check_input_safety(user_input: str) -> tuple[bool, str]:
    """
    Returns (is_safe, reason).
    Blocks requests containing sensitive/unsafe keywords.
    """
    lower_input = user_input.lower()
    for keyword in BLOCKED_KEYWORDS:
        if keyword in lower_input:
            return False, f"Request blocked: contains restricted term '{keyword}'"
    return True, ""


def check_output_safety(agent_response: str) -> tuple[bool, str]:
    """
    Basic check on agent output before returning to user.
    """
    if len(agent_response) > 5000:
        return False, "Response blocked: exceeds maximum length"
    return True, ""


