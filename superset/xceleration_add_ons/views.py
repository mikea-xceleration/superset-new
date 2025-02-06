import traceback
import uuid
from typing import Any, Optional

from flask import request, session, redirect
from flask_appbuilder import expose
from flask_appbuilder.security.views import AuthDBView

import logging

from flask_appbuilder.utils.base import get_safe_redirect
from flask_login import current_user

logger = logging.getLogger(__name__)


class DualAuthView(AuthDBView):
    def __init__(self):
        logger.info("Initializing DualAuthView")
        super().__init__()

    @expose('/login', methods=['GET', 'POST'])
    def login(self) -> Any:
        request_id = str(uuid.uuid4())
        logger.info(
            "Processing login request: "
            f"request_id={request_id}, "
            f"user_agent={request.user_agent.string}, "
            f"remote_addr={request.remote_addr}"
        )
        try:

            token = None
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            else:
                # Try to get token from request body, query parameter, or next URL
                token = (
                    request.json.get('token') if request.is_json else None
                                                                      or request.args.get(
                        'token')
                                                                      or self._extract_token_from_next_param()
                )

            if not token:
                logger.info(
                    "No token provided in session login request: "
                    f"request_id={request_id}"
                )
                return self._login_with_standard(request_id)
            else:
                logger.info("token provided in session login request: "
                            f"request_id={request_id}")
                return self._login_with_token(request_id, token)
        except Exception as e:
            logger.error(
                f"Error during login: "
                f"request_id={request_id}, "
                f"error={str(e)}, "
                f"traceback={traceback.format_exc()}"
            )
            raise

    def _login_with_standard(self, request_id: str) -> Any:
        logger.info(
            "Using standard login"
            f"request_id={request_id}"
        )
        result = super().login()
        logger.info(
            f"Standard login result: "
            f"request_id={request_id}, "
            "success=True"
        )
        return result

    def _login_with_token(self, request_id, token):
        logger.info(
            "Using token login"
            f"request_id={request_id}"
        )
        success = self.appbuilder.sm.auth_jwt_login(token, request_id)
        if success:
            session.permanent = True
            session['token'] = token
            self.appbuilder.get_session.commit()

            # Create a response with session cookie
            logger.info(
                f"Bearer token authentication result: "
                f"request_id={request_id}, "
                f"user_id={current_user.id}, "
                f"session_id={session.get('_id')}"
            )
            next_url = get_safe_redirect(request.args.get("next", ""))
            return redirect(next_url)
        else:
            logger.warning(
                "Invalid token in session login request: ",
                f"request_id={request_id}"
            )
            error_msg = {"message": "Authentication failed"}
            return self.json_response(error_msg, 401)

    def _extract_token_from_next_param(self) -> Optional[str]:
        """Extract token from the 'next' parameter if present."""
        next_url = request.args.get('next')
        if not next_url:
            return None

        try:
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(next_url)
            query_params = parse_qs(parsed.query)

            # Get token from query parameters
            tokens = query_params.get('token')
            if tokens and len(tokens) > 0:
                return tokens[0]
        except Exception as e:
            logger.warning(f"Error extracting token from next parameter: {str(e)}")

        return None
