def calculator(expression: str) -> str:
    """
    Safely evaluates a basic math expression.
    Supports +, -, *, /, and parentheses.
    """
    allowed_chars = set("0123456789+-*/(). ")
    if not all(c in allowed_chars for c in expression):
        return "Error: Expression contains invalid characters."
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error: {e}"


# Registry of available tools
TOOLS = {
    "calculator": calculator,
}