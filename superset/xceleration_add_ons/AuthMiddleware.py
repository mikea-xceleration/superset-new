from typing import Any, Optional
import uuid
import json
import logging
from superset.extensions import appbuilder
from superset import app
from flask import request, g, current_app

logger = logging.getLogger(__name__)


class AuthMiddleware:
    def __init__(self, app: Any):
        self.app = app
        self.exempt_paths = ('/static', '/healthz')

    def __call__(self, environ, start_response):
        def authenticate_response(status: str, headers: list[tuple[str, str]],
                                  exc_info: None | tuple = None) -> list[bytes]:

            request_id = self._generate_request_id()
            self._log_request(request_id)

            if self._is_login_endpoint():
                return self._handle_login_endpoint(environ, start_response, status,
                                                   headers, exc_info, request_id)

                if self._is_exempt_path():
                    return self.app(environ, start_response)

                return self._handle_standard_request(environ, start_response, headers,
                                                     request_id)

        return self.app(environ, authenticate_response)

    def _generate_request_id(self) -> str:
        return str(uuid.uuid4())

    def _log_request(self, request_id: str) -> None:
        logger.info(
            f"Processing request path={request.path} method={request.method}"
            f"[request_id={request_id}]"
        )

    def _is_login_endpoint(self) -> bool:
        return request.path == '/api/v1/security/login'

    def _is_exempt_path(self) -> bool:
        return any(request.path.startswith(path) for path in self.exempt_paths)

    def _get_bearer_token(self) -> Optional[str]:
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]
        return None

    def _send_response(self, start_response, status: str, body: Any,
                       request_headers: list[tuple[str, str]],
                       content_type: str = 'text/plain'):
        """Directly send a response without calling the next middleware"""
        if isinstance(body, (dict, list)):
            body = json.dumps(body)
        if not isinstance(body, bytes):
            body = body.encode('utf-8')

        headers = [
            ('Content-Type', content_type),
            ('Content-Length', str(len(body)))
        ]

        # Merge custom headers with default headers
        headers.extend(request_headers)

        # Merge the default headers with the request headers
        # Convert to dictionary to automatically remove duplicates
        header_dict = dict(headers)  # Convert default headers to a dictionary
        header_dict.update(
            request_headers)
        # Update with custom headers (this will overwrite duplicates)

        start_response(status, list(header_dict.items()))
        return [body]

    def _authenticate_token(self, token: str, request_id: str) -> bool:
        with app.app_context():
            security_manager = appbuilder.sm
            return security_manager.auth_jwt_login(token, request_id)

    def _handle_login_endpoint(self, environ, start_response,
                               status: str, headers: list[tuple[str, str]],
                               exc_info: None | tuple, request_id: str):
        token = self._get_bearer_token()
        if not token:
            # No token, let the regular login flow handle it
            return self.app(environ, start_response)

        if self._authenticate_token(token, request_id):
            response_data = {
                "access_token": "access_token",
            }
            # Send direct response for successful JWT login
            return self._send_response(
                start_response,
                '200 OK',
                response_data,
                headers,
                'application/json'
            )

        # Send direct 401 response for failed JWT auth
        return self._send_response(
            start_response,
            '401 Unauthorized',
            'Unauthorized',
            headers
        )

    def _handle_standard_request(self, environ, start_response,
                                 headers: list[tuple[str, str]], request_id: str):
        token = self._get_bearer_token()
        if not token:
            # No token, continue the middleware chain
            return self.app(environ, start_response)

        if not self._authenticate_token(token, request_id):
            # Failed JWT auth, send direct 401 response
            return self._send_response(
                start_response,
                '401 Unauthorized',
                'Unauthorized',
                headers
            )

        # Token authenticated, continue the middleware chain
        return self.app(environ, start_response)
