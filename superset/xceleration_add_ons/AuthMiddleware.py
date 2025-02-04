from typing import Any
import uuid
import logging
from superset.extensions import appbuilder
from superset import app
from flask import request, Response

logger = logging.getLogger(__name__)


class AuthMiddleware:
    def __init__(self, app: Any):
        self.app = app

    def __call__(self, environ, start_response):
        def authenticate_response(status, headers, exc_info=None):
            request_id = str(uuid.uuid4())
            path = request.path
            logger.info(
                f"Processing request path={path} method={request.method}"
                f"[request_id={request_id}]"
            )

            if path.startswith(('/static', '/healthz')):
                logger.debug(
                    f"Skipping auth for exempt path {request.path} "
                    f"[request_id={request_id}]")
                return start_response(status, headers, exc_info)

            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                with app.app_context():
                    security_manager = appbuilder.sm
                    if not security_manager.auth_jwt_login(token, request_id):
                        logger.warning(
                            f"JWT authentication failed [request_id={request_id}]")
                        return start_response('401',
                                              [('Content-Type', 'text/plain')],
                                              exc_info)

            # return start_response('200', headers, exc_info)
            return self.app(environ, start_response)

        return self.app(environ, authenticate_response)
