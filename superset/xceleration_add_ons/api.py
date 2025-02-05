import traceback
import uuid

from flask import request, session
from flask_appbuilder import expose
from flask_appbuilder.api import safe, BaseApi
from flask_appbuilder.security.views import AuthView
from flask_login import current_user, logout_user

import logging

from superset.superset_typing import FlaskResponse

logger = logging.getLogger(__name__)


class BearerTokenApi(BaseApi):
    resource_name = "auth"
    base_api_path = '/api/v1/auth'

    @expose('login', methods=['GET', 'POST'])
    @safe
    def login(self) -> FlaskResponse:
        # with self.appbuilder.app.app_context():
        request_id = str(uuid.uuid4())
        logger.info(
            "Processing bearer token login request: "
            f"request_id={request_id}, "
            f"user_agent={request.user_agent.string}, "
            f"remote_addr={request.remote_addr}"
        )
        # Check if already authenticated
        if current_user.is_authenticated:
            logger.debug(
                "User already authenticated: "
                f"request_id={request_id}, "
                f"user_id={current_user.id}"
            )
            logger.debug("Loging out user")
            logout_user()
        # Get token from request
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        else:
            # Try to get token from request body or query parameter
            token = request.json.get('token') or request.args.get('token')

        if not token:
            logger.warning(
                "No token provided in session login request: "
                f"request_id={request_id}"
            )
            return self.response_401()
        try:
            success = self.appbuilder.sm.auth_jwt_login(token, request_id)
            if success:
                session.permanent = True
                self.appbuilder.get_session.commit()

                # Create a response with session cookie
                logger.info(
                    f"Bearer token authentication result: "
                    f"request_id={request_id}, "
                    f"user_id={current_user.id}, "
                    f"session_id={session.get('_id')}"
                )
                return self.response(200,
                                     **{"message": "Authentication successful"})
            else:
                logger.warning(
                    "Invalid token in session login request: ",
                    f"request_id={request_id}"
                )
                return self.response_401()
        except Exception as e:
            logger.error(
                f"Error during bearer token authentication: "
                f"request_id={request_id}, "
                f"error={str(e)}, "
                f"traceback={traceback.format_exc()}"
            )
            return self.response_401()

    @expose('/v1/auth/check/', methods=['GET'])
    def check_session(self) -> FlaskResponse:
        # with self.appbuilder.app.app_context():
        """Endpoint to check current session status"""
        if current_user.is_authenticated:
            return self.json_response({
                "status": "success",
                "authenticated": True,
                "user": current_user.username
            }, 200)
        return self.response_401()
