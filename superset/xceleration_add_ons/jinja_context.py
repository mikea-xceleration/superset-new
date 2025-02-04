from typing import Dict, Any, Optional
from flask import session
from markupsafe import escape


def oauth_value(
    claim: str,
    escape_result: bool,
    default: Optional[str] = None
) -> Optional[str]:
    result = session.get(claim)
    if result is None:
        result = default

    if result is not None and escape_result:
        return escape(str(result))

    return result


# Add this to your custom_jinja_context.py
def xceleration_jinja_context() -> Dict[str, Any]:
    context: Dict[str, Any] = {
        'oauth_value': oauth_value
    }

    return context
