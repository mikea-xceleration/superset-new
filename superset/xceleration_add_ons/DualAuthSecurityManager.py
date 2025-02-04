from typing import Dict, Any

from flask_appbuilder.security.views import AuthDBView
from flask_appbuilder.security.sqla.models import User, Role
from flask import session, request, g
from flask_login import login_user, logout_user
from datetime import datetime, tzinfo

import logging

from superset import SupersetSecurityManager
from superset.xceleration_add_ons.utils import OIDCConfig, TokenValidator

logger = logging.getLogger(__name__)


class DualAuthSecurityManager(SupersetSecurityManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Keep the standard database auth view for login screen
        self.authdbview = AuthDBView
        self.oidc_config = OIDCConfig()
        self.token_validator = TokenValidator(self.oidc_config)

    def auth_jwt_login(self, token: str, request_id: str) -> bool:
        try:
            response = self.token_validator.validate_token(token, request_id)
            if not response.is_valid:
                return False
            if not self.token_validator.validate_scope(response.decoded_token, request_id):
                return False
            guest_role = self.__get_or_create_guest_role(request_id)
            guest_user = self.__get_or_create_guest_user(guest_role, request_id)

            # Update last login
            guest_user.last_login = datetime.now()
            self.get_session.merge(guest_user)
            self.get_session.commit()

            # self.update_user_auth_stat(guest_user)
            self.__update_session(response.decoded_token)
            # logout_user()
            login_user(guest_user, remember=False)

            return True
        except Exception as e:
            logger.error(f"Error in auth_jwt_login: {str(e)} [request_id={request_id}]")
            return False

    def __get_or_create_guest_user(self, guest_role: Role, request_id: str) -> User:
        guest_user = self.find_user(username='guest')
        if not guest_user:
            logger.info(
                "Guest user not found, creating new guest user"
                "[request_id=%(request_id)s]",
                {"request_id": request_id}
            )
            guest_user = self.add_user(
                username='guest',
                first_name='Guest',
                last_name='User',
                email='guest@example.com',
                role=guest_role
            )

        return guest_user

    def __get_or_create_guest_role(self, request_id: str) -> Role:
        guest_role = self.find_role("Guest")
        if not guest_role:
            logger.info(
                "Guest role not found, creating new guest role "
                "[request_id=%(request_id)s]",
                {"request_id": request_id}
            )
            guest_role = self.add_role("Guest")

            permissions: list[tuple[str, str]] = [
                ("can_read", "Dashboard"),
                ("can_read", "Chart"),
            ]

            for permission in permissions:
                perm_view = self.find_permission_view_menu(*permission)
                if perm_view:
                    self.add_permission_role(guest_role, perm_view)
                    logger.debug(
                        "Added permission %(permission)s to Guest role "
                        "[request_id=%(request_id)s]",
                        {"request_id": request_id, "permission": permission}
                    )

        return guest_role

    def __update_session(self, decoded_token: Dict[Any, Any]):
        """Updates session with token claims."""
        allowed_claims = ['clientId', 'userId', 'repTypeId', 'sub', 'email', 'name',
                          'given_name', 'family_name']
        for claim in allowed_claims:
            if claim in decoded_token:
                logger.debug(f"Adding claim - {claim} to session")
                session[claim] = decoded_token[claim]

