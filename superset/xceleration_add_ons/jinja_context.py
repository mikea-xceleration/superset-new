from typing import Dict, Any, Optional
from flask import session
from markupsafe import escape
import logging

logger = logging.getLogger(__name__)


def oauth_value(
    claim: str,
    should_escape: bool,
    default_value: Optional[str] = None
) -> Optional[str]:
    logger.info(f"Accessing OAuth claim: {claim}")
    claim_value = session.get(claim)

    if claim_value is None:
        logger.debug(f"Claim {claim} not found in session, using default: {default_value}")
        claim_value = default_value
    else:
        logger.debug(f"Found value for claim {claim} in session")

    if claim_value is not None and should_escape:
        logger.debug(f"Escaping result for claim {claim}")
        return escape(str(claim_value))

    return claim_value


def xceleration_jinja_context() -> Dict[str, Any]:
    logger.info("Creating Jinja context")
    jinja_context: Dict[str, Any] = {
        'oauth_value': oauth_value
    }
    logger.debug(f"Created context with {len(jinja_context)} functions")
    return jinja_context
