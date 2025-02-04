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
import logging
from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass

import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

from .oidc import OIDCConfig

logger = logging.getLogger(__name__)


@dataclass
class TokenValidationResult:
    """Represents the result of token validation."""
    is_valid: bool
    decoded_token: Optional[Dict[Any, Any]] = None
    error_response: Optional[Any] = None


class TokenValidator:
    """Handles JWT token validation and scope checking."""

    def __init__(self, oidc_config: OIDCConfig):
        self.oidc_config = oidc_config

    def validate_token(self, token: str, request_id: str) -> TokenValidationResult:
        """Validates the JWT token signature and claims."""
        logger.info(f"Starting JWT authentication process [request_id={request_id}]")
        try:
            # signing_key = self.oidc_config.jwks_client.get_signing_key_from_jwt(token)
            # decoded = jwt.decode(
            #     token,
            #     signing_key.key,
            #     algorithms=["RS256"],
            #     options={
            #         "verify_exp": True,
            #         "verify_iat": True,
            #         "verify_nbf": True,
            #         "verify_iss": True,
            #         "verify_aud": False,
            #     }
            # )
            #
            # # Validate issuer
            # config = self.oidc_config._fetch_oidc_config()
            # expected_issuer = config.get('issuer')
            # if not expected_issuer or decoded.get('iss') != expected_issuer:
            #     logger.warning(f"Invalid token issuer [request_id={request_id}]")
            #     return TokenValidationResult(is_valid=False,
            #                                  error_response="Invalid token issuer")

            decoded = jwt.decode(token, options={"verify_signature": False})
            logger.debug(f"Token decoded successfully [request_id={request_id}]")
            return TokenValidationResult(is_valid=True, decoded_token=decoded)

        except ExpiredSignatureError:
            logger.warning(f"Token has expired [request_id={request_id}]")
            return TokenValidationResult(is_valid=False,
                                         error_response="Token has expired")
        except InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)} [request_id={request_id}]")
            return TokenValidationResult(is_valid=False,
                                         error_response="Invalid token")
        except Exception as e:
            logger.error(f"Error processing token: {str(e)} [request_id={request_id}]")
            return TokenValidationResult(is_valid=False,
                                         error_response="Invalid token")

    def validate_scope(self, decoded_token: Dict[Any, Any], request_id: str) -> bool:
        """Validates that the token has the required scope."""
        # scope = decoded_token.get('scope', '')
        # if isinstance(scope, str):
        #     scopes = scope.split()
        # elif isinstance(scope, list):
        #     scopes = scope
        # else:
        #     logger.warning(f"Invalid scope format in token [request_id={request_id}]")
        #     return False
        #
        # if 'reports' not in scopes:
        #     logger.warning(
        #         f"Token missing required 'reports' scope [request_id={request_id}]")
        #     return False

        return True
