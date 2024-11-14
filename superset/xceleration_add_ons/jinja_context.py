from typing import Optional
from flask import has_request_context, request, session

from superset import results_backend


def oauth_value(
    claim: str,
    default: Optional[str] = None,
    escape_result: bool = True,
) -> Optional[str]:
    # pylint: disable=import-outside-toplevel

    # if has_request_context() and request.args.get(param):
    #     return request.args.get(param, default)
    # 
    
    result = session.get(claim)
    if result is None:
        result = default
    
    return result
    # return "2472059"
