from typing import Optional, Any, Tuple, List
from flask import session, request
from flask_login import current_user, logout_user
from urllib.parse import urlencode
from superset.xceleration_add_ons.utils import extract_token_from_request

import logging

logger = logging.getLogger(__name__)


class TokenAuthMiddleware:
    # Extracted constants for clarity
    LOGIN_PATH = '/login'
    CACHE_HEADERS = [
        ('Cache-Control', 'no-cache, no-store, must-revalidate'),
        ('Pragma', 'no-cache'),
        ('Expires', '0'),
    ]
    EXCLUDED_PATHS = ['/static/', '/api/', '/health']

    def __init__(self, app: Any) -> None:
        self.app = app
        logger.info("TokenAuthMiddleware initialized")

    def __call__(self, environ: dict, start_response: Any) -> Any:
        return self.app(environ, self._create_response_handler(start_response))

    def _create_response_handler(self, start_response: Any) -> Any:
        def middleware_response(status: str, headers: List[Tuple[str, str]],
                                exc_info=None) -> Any:
            try:
                logger.debug("token_auth_middleware called")
                if not self._should_redirect():
                    return start_response(status, headers, exc_info)

                token = extract_token_from_request(request)
                if not (token and current_user.is_authenticated and
                        self._should_logout(token)):
                    return start_response(status, headers, exc_info)

                # We want to log out the user and redirect
                self._logout_current_user()
                redirect_url = self._build_redirect_url()
                return start_response(
                    '302 Found',
                    [('Location', redirect_url)] + self.CACHE_HEADERS,
                    exc_info
                )
            except Exception as e:
                logger.error(f"Error in token auth middleware: {e}")
                return start_response(status, headers, exc_info)

        return middleware_response

    def _should_redirect(self) -> bool:
        """Decide if the request needs a redirect based on its path."""
        if request.path.endswith(self.LOGIN_PATH):
            return False
        if any(request.path.startswith(prefix) for prefix in self.EXCLUDED_PATHS):
            return False
        return True

    def _build_redirect_url(self) -> str:
        """Construct the fully qualified redirect URL."""
        query_args = dict(request.args)
        query_args['force'] = 'true'
        next_url = request.path
        if query_args:
            next_url = f"{request.path}?{urlencode(query_args)}"
        return f"{self.LOGIN_PATH}?{urlencode({'next': next_url})}"



    @staticmethod
    def _should_logout(token: str) -> bool:
        """Check if the current session token differs from the provided token."""
        try:
            current_token = session.get('token')
            if current_token != token:
                logger.info("Token change detected, transitioning user")
                return True
            return False
        except Exception as e:
            logger.error(f"Error comparing session token: {e}")
            return False

    @staticmethod
    def _logout_current_user() -> None:
        """Safely log out current user."""
        try:
            session.clear()
            logout_user()
            logger.info("Successfully logged out current user")
        except Exception as e:
            logger.error(f"Error during user logout: {e}")
            raise
