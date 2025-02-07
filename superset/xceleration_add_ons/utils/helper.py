from typing import Optional
import logging

logger = logging.getLogger(__name__)
BEARER_PREFIX = 'Bearer '
TOKEN_KEY = 'token'


def extract_token_from_request(request, check_next_url: bool = False) -> Optional[str]:
    """
    Extract a token from the current request.
    The function searches in:
      1) Authorization header with the Bearer prefix
      2) Query parameter named 'token'
      3) JSON body field named 'token'
    """
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith(BEARER_PREFIX):
        bearer_token = auth_header[len(BEARER_PREFIX):]
        return bearer_token

    token_query_param = request.args.get(TOKEN_KEY)
    if token_query_param:
        return token_query_param

    if request.is_json:
        body_payload = request.get_json(silent=True) or {}
        if TOKEN_KEY in body_payload:
            return body_payload.get(TOKEN_KEY)

    if check_next_url:
        return _extract_token_from_next_url(request)

    return None


def _extract_token_from_next_url(request) -> Optional[str]:
    """Extract token from the 'next' parameter if present."""
    next_url = request.args.get('next')
    if not next_url:
        return None
    try:
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(next_url)
        query_params = parse_qs(parsed.query)
        tokens = query_params.get(TOKEN_KEY)
        if tokens and len(tokens) > 0:
            return tokens[0]
    except Exception as e:
        logger.warning(f"Error extracting token from next parameter: {str(e)}")
    return None

