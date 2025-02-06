from typing import Dict, Any, Optional
from flask import session, g
from markupsafe import escape
import logging

# Configure logger
logger = logging.getLogger(__name__)

def oauth_value(
    claim: str,
    escape_result: bool,
    default: Optional[str] = None
) -> Optional[str]:
    logger.info(f"Accessing OAuth claim: {claim}")

    # Log all session values
    # logger.debug("Current session values:")
    # for key, value in session.items():
    #     # Mask sensitive values like tokens or personal info
    #     if any(sensitive in key.lower() for sensitive in ['token', 'password', 'secret', 'key']):
    #         logger.debug(f"  {key}: [MASKED]")
    #     else:
    #         logger.debug(f"  {key}: {value}")

    result = session.get(claim)
    if result is None:
        logger.debug(f"Claim {claim} not found in session, using default: {default}")
        result = default
    else:
        logger.debug(f"Found value for claim {claim} in session")

    if result is not None and escape_result:
        logger.debug(f"Escaping result for claim {claim}")
        return escape(str(result))

    return result


# Add this to your custom_jinja_context.py
def xceleration_jinja_context() -> Dict[str, Any]:
    logger.info("Creating Jinja context")
    context: Dict[str, Any] = {
        'oauth_value': oauth_value
    }
    logger.debug(f"Created context with {len(context)} functions")
    return context
