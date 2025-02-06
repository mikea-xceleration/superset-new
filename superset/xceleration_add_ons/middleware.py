from typing import Optional, Tuple

import jwt
from flask import session, request, g, Response
from flask_login import current_user, logout_user
from urllib.parse import urlparse, parse_qs, urlencode
import logging

logger = logging.getLogger(__name__)


class TokenAuthMiddleware:
    def __init__(self, app):
        self.app = app
        logger.info("TokenAuthMiddleware initialized")

    def __call__(self, environ, start_response):
        def token_auth_start_response(status, headers, exc_info=None):
            # Create a context for Flask request processing
            logger.debug("TokenAuthMiddleware checking request")

            try:
                if not self._should_redirect():
                    return start_response(status, headers, exc_info)

                logger.debug("request.path: " + request.path)
                token = self._extract_token()
                if token and current_user.is_authenticated:
                    logger.debug(
                        "Found token in request, checking session compatibility")

                    if self._should_logout(token):
                        logger.info(
                            "Session mismatch detected, logging out current user")
                        self._logout_current_user()
                        # Get the current path and add force=true
                        base_path = request.path
                        query_params = dict(request.args)
                        query_params['force'] = 'true'

                        # Build the next URL with encoded parameters
                        next_url = base_path
                        if query_params:
                            next_url = f"{base_path}?{urlencode(query_params)}"

                        # Encode the entire next URL for the login redirect
                        redirect_params = {'next': next_url}
                        redirect_url = f"/login?{urlencode(redirect_params)}"

                        return start_response('302 Found', [
                            ('Location', redirect_url),
                            ('Cache-Control', 'no-cache, no-store, must-revalidate'),
                            ('Pragma', 'no-cache'),
                            ('Expires', '0')
                        ])
                return start_response(status, headers, exc_info)
            except Exception as e:
                logger.error(f"Error in token auth middleware: {str(e)}")
                return start_response(status, headers, exc_info)

        # Continue with the request
        return self.app(environ, token_auth_start_response)

    def _has_token_in_request(self) -> bool:
        """Check if the request has a token in various locations."""
        if self._check_authorization_header():
            return True

        if self._check_request_parameters():
            return True

        if self._check_json_body():
            return True

        logger.debug("No token found in request")
        return False

    def _check_authorization_header(self) -> bool:
        """Check for token in Authorization header."""
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            logger.debug("Found token in Authorization header")
            return True
        return False

    def _check_request_parameters(self) -> bool:
        """Check for token in request parameters."""
        if request.args.get('token'):
            logger.debug("Found token in query parameters")
            return True
        return False

    def _check_json_body(self) -> bool:
        """Check for token in JSON request body."""
        if request.is_json and request.get_json(silent=True):
            json_data = request.get_json(silent=True)
            if json_data and json_data.get('token'):
                logger.debug("Found token in JSON body")
                return True
        return False

    def _logout_current_user(self) -> None:
        """Safely log out the current user."""
        try:
            session.clear()
            logout_user()
            logger.info("Successfully logged out current user")
        except Exception as e:
            logger.error(f"Error during user logout: {str(e)}")
            raise

    def _extract_token(self) -> Optional[str]:
        """Extract token from request if present."""
        # Check Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            logger.debug("Found token in Authorization header")
            return auth_header.split(' ')[1]

        # Check request parameters
        if request.args.get('token'):
            logger.debug("Found token in query parameters")
            return request.args.get('token')

        # Check JSON body
        if request.is_json and request.get_json(silent=True):
            json_data = request.get_json(silent=True)
            if json_data and json_data.get('token'):
                logger.debug("Found token in JSON body")
                return json_data.get('token')

        return None

    def _handle_redirect(self, start_response, status, headers, exc_info) -> list:
        """Handle the redirect to login page with next parameter."""
        try:
            # Get the full path including query string
            next_url = request.full_path

            # Build login URL with parameters
            params = {'next': next_url}

            # # Add token if present
            # token = self._extract_token()
            # if token:
            #     params['token'] = token

            # Construct login redirect URL
            redirect_url = f"/login?{urlencode(params)}"

            # Create redirect response
            response = Response(
                '',
                302,
                {
                    'Location': redirect_url,
                    'Cache-Control': 'no-cache, no-store, must-revalidate',
                    'Pragma': 'no-cache',
                    'Expires': '0'
                }
            )

            logger.info(f"Redirecting to: {redirect_url}")
            return start_response(302, [
                ('Location', redirect_url),
                ('Cache-Control', 'no-cache, no-store, must-revalidate'),
                ('Pragma', 'no-cache'),
                ('Expires', '0')
            ], exc_info)

        except Exception as e:
            logger.error(f"Error handling redirect: {str(e)}")

            return start_response(401, headers, exc_info)

    def _should_redirect(self) -> bool:
        """Check if the request should be redirected."""
        # Don't redirect if already on login page
        if request.path.endswith('/login'):
            return False

        # Don't redirect for static files or certain endpoints
        if any(request.path.startswith(prefix) for prefix in
               ['/static/', '/api/', '/health']):
            return False

        return True

    def _should_logout(self, token: str) -> bool:
        """
        Determine if user should be logged out based on token and session comparison.
        Returns True if either client_id or user_id differs between token and session.
        """
        try:
            logger.debug("Checking session and token for mismatch")
            current_token = session.get('token')
            logger.debug(f"Current token: {current_token}")
            logger.debug(f"Token from request: {token}")
            if current_token != token:
                logger.info("Token change detected, transitioning user")
                return True
            logger.debug("Session and token IDs match")
            return False

        except Exception as e:
            logger.error(f"Error comparing session and token: {str(e)}")
            return False
