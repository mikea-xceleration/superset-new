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
from typing import Optional
import requests
from flask import current_app
from jwt import PyJWKClient
from urllib.parse import urljoin
from cachetools import TTLCache

logger = logging.getLogger(__name__)


class OIDCConfig:
    """Handles OIDC configuration and JWKS client management."""

    def __init__(self):
        self._jwks_client: Optional[PyJWKClient] = None
        self._config_cache = TTLCache(maxsize=1, ttl=3600)

    def _fetch_oidc_config(self):
        """Fetches and caches OIDC configuration from the well-known endpoint."""
        if 'config' not in self._config_cache:
            try:
                oidc_url = current_app.config.get('OIDC_ISSUER')
                if not oidc_url:
                    raise RuntimeError("OIDC_ISSUER not configured in Superset config")

                wellknown_url = urljoin(oidc_url, '.well-known/openid-configuration')
                response = requests.get(wellknown_url)
                response.raise_for_status()
                self._config_cache['config'] = response.json()
            except requests.RequestException as e:
                logger.error(f"Failed to fetch OIDC configuration: {e}")
                raise RuntimeError("Failed to fetch OIDC configuration")
        return self._config_cache['config']

    @property
    def jwks_client(self) -> PyJWKClient:
        """Returns a configured JWKS client for token validation."""
        if self._jwks_client is None:
            config = self._fetch_oidc_config()
            jwks_uri = config.get('jwks_uri')
            if not jwks_uri:
                raise RuntimeError("JWKS URI not found in OIDC configuration")
            self._jwks_client = PyJWKClient(jwks_uri)
        return self._jwks_client
