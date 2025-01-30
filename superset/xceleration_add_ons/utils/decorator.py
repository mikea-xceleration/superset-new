# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
import functools
import logging
from typing import Optional, Dict, Any, Tuple
from flask import session, request
from flask_login import login_user, logout_user

from .oidc import OIDCConfig
from .token import TokenValidator

logger = logging.getLogger(__name__)


class ImpersonationDecorator:
    """Handles user impersonation with OIDC token validation."""

    def __init__(self, username: str):
        self.username = username
        self.oidc_config = OIDCConfig()
        self.token_validator = TokenValidator(self.oidc_config)

    def validate_request(self, view_instance) -> Tuple[
        bool, Optional[Dict], Optional[Any]]:
        """Validates the incoming request and token."""
        token = request.args.get('token')
        if token is None:
            logger.warning("No token provided in request")
            return False, None, view_instance.response_401()

        validation_result = self.token_validator.validate_token(token, view_instance)
        if not validation_result.is_valid:
            return False, None, validation_result.error_response

        is_scope_valid, scope_error = self.token_validator.validate_scope(
            validation_result.decoded_token, view_instance)
        if not is_scope_valid:
            return False, None, scope_error

        return True, validation_result.decoded_token, None

    def setup_user(self, view_instance) -> Tuple[bool, Optional[Any]]:
        """Sets up user impersonation."""
        user = view_instance.appbuilder.sm.find_user(username=self.username)
        if not user:
            logger.warning(f"User {self.username} not found")
            return False, view_instance.response_401()

        logout_user()
        login_user(user, remember=False)
        return True, None

    def update_session(self, decoded_token: Dict[Any, Any], view_instance):
        """Updates session with token claims."""
        session.clear()
        allowed_claims = ['clientId', 'userId', 'repTypeId', 'sub', 'email', 'name',
                          'given_name', 'family_name']
        for claim in allowed_claims:
            if claim in decoded_token:
                session[claim] = decoded_token[claim]

        session['csrf_token'] = view_instance.appbuilder.sm.get_csrf_token()

    def __call__(self, f):
        @functools.wraps(f)
        def wraps(view_instance, *args, **kwargs):
            # Validate request and token
            is_valid, decoded_token, error = self.validate_request(view_instance)
            if not is_valid:
                return error

            # Set up user impersonation
            is_setup_ok, setup_error = self.setup_user(view_instance)
            if not is_setup_ok:
                return setup_error

            # Update session with claims
            self.update_session(decoded_token, view_instance)

            logger.info(f"Successfully impersonated user {self.username}")
            return f(view_instance, *args, **kwargs)

        return wraps
