import traceback
import uuid
from typing import Any, Optional
from flask import request, session, redirect
from flask_appbuilder import expose
from flask_appbuilder.security.views import AuthDBView
import logging
from flask_appbuilder.utils.base import get_safe_redirect
from flask_login import current_user
from superset.xceleration_add_ons.utils import extract_token_from_request

logger = logging.getLogger(__name__)


class DualAuthView(AuthDBView):
    def __init__(self):
        logger.info("Initializing DualAuthView")
        super().__init__()

    @expose('/login', methods=['GET', 'POST'])
    def login(self) -> Any:
        request_id = str(uuid.uuid4())
        user_agent = request.user_agent.string
        remote_addr = request.remote_addr
        logger.info(
            "Processing login request: "
            f"request_id={request_id}, "
            f"user_agent={user_agent}, "
            f"remote_addr={remote_addr}"
        )
        try:
            auth_token = extract_token_from_request(request, True)
            if not auth_token:
                logger.info(
                    "No token provided in session login request: "
                    f"request_id={request_id}"
                )
                return self._perform_standard_login(request_id)
            else:
                logger.info(
                    "Token provided in session login request: "
                    f"request_id={request_id}"
                )
                return self._perform_token_login(request_id, auth_token)
        except Exception as e:
            logger.error(
                "Error during login: "
                f"request_id={request_id}, "
                f"error={str(e)}, "
                f"traceback={traceback.format_exc()}"
            )
            raise

    def _perform_standard_login(self, request_id: str) -> Any:
        logger.info(f"Using standard login request_id={request_id}")
        result = super().login()
        logger.info(f"Standard login result: request_id={request_id}, success=True")
        return result

    def _perform_token_login(self, request_id: str, token: str) -> Any:
        logger.info(f"Using token login request_id={request_id}")
        success = self.appbuilder.sm.authenticate_jwt(token, request_id)
        if success:
            session.permanent = True
            session['token'] = token
            self.appbuilder.get_session.commit()
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
                "Invalid token in session login request: "
                f"request_id={request_id}"
            )
            error_msg = {"message": "Authentication failed"}
            return self.json_response(error_msg, 401)

    @staticmethod
    def _get_token_from_next() -> Optional[str]:
        """Extract token from the 'next' parameter if present."""
        next_url = request.args.get('next')
        if not next_url:
            return None
        try:
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(next_url)
            query_params = parse_qs(parsed.query)
            tokens = query_params.get('token')
            if tokens and len(tokens) > 0:
                return tokens[0]
        except Exception as e:
            logger.warning(f"Error extracting token from next parameter: {str(e)}")
        return None
