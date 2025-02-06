from urllib.parse import urlparse, parse_qs

from superset.security import SupersetSecurityManager
from flask_login import login_user, logout_user
from flask import session, request, g
from flask_appbuilder.security.sqla.models import User, Role

from superset.xceleration_add_ons.views import DualAuthView

import traceback
import logging

from superset.xceleration_add_ons.utils import OIDCConfig, TokenValidator

logger = logging.getLogger(__name__)


class BearerAuthSecurityManager(SupersetSecurityManager):
    def __init__(self, *args, **kwargs):
        logger.info("Initializing BearerAuthSecurityManager")
        super().__init__(*args, **kwargs)
        self.authdbview = DualAuthView
        self.oidc_config = OIDCConfig()
        self.token_validator = TokenValidator(self.oidc_config)
        logger.info("BearerAuthSecurityManager initialized")

    def auth_jwt_login(self, token: str, request_id: str) -> bool:
        try:
            response = self.token_validator.validate_token(token, request_id)
            if not response.is_valid:
                logger.warning(f"Invalid token validation [request_id={request_id}]")
                return False
            if not self.token_validator.validate_scope(response.decoded_token,
                                                       request_id):
                logger.warning(f"Invalid token scope [request_id={request_id}]")
                return False

            guest_role = self._get_or_create_guest_role(request_id)
            guest_user = self._get_or_create_guest_user(guest_role, request_id)

            if not guest_user:
                logger.warning(f"User not found: [request_id]={request_id}")
                return False

            is_logged_in = login_user(guest_user)

            logger.debug(f"User logged in: {is_logged_in}")
            for key, value in response.decoded_token.items():
                session[key] = value
                logger.debug(f"Adding claim - {key} to session")

            logger.info(
                "Bearer token authenticated successfully: "
                f"request_id={request_id}, "
                f"user_id={guest_user.id}, "
                f"session_id={session.get('_id')}"
            )
            return True

        except Exception as e:
            f"request_id={request_id}, "
            f"error={str(e)}, "
            f"traceback={traceback.format_exc()}"
            return False

    def _get_or_create_guest_user(self, guest_role: Role, request_id: str) -> User:
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

    def _get_or_create_guest_role(self, request_id: str) -> Role:
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
                ("can_dashboard", "Superset"),
                ("can_read", "DashboardFilterStateRestApi"),
                ("can_read", "DashboardPermalinkRestApi")
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



