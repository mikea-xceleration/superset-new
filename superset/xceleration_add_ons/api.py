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
import urllib.parse
import jwt
from flask import request, Response, redirect
from flask_appbuilder import expose
from flask_appbuilder.api import safe

from superset.extensions import event_logger
from superset.utils.urls import get_url_host
from superset.views.base_api import BaseSupersetApi, BaseSupersetModelRestApi, \
    statsd_metrics
from superset.xceleration_add_ons.decorators import impersonate

logger = logging.getLogger(__name__)


class XcelerationRestApi(BaseSupersetApi):
    resource_name = "xcel"
    allow_browser_login = True
    openapi_spec_tag = "Xceleration"

    @expose('/sso/', methods=("GET",))
    @event_logger.log_this
    @impersonate('Guest')
    @safe
    @statsd_metrics
    def sso(self) -> Response:
        logger.info('Using Embedded Auth Views')
        dashboard = request.args.get('dashboard')
        parsed_url = urllib.parse.urlparse(request.base_url)
        redirect_url = \
            (f'{parsed_url.scheme}://{parsed_url.hostname}:{parsed_url.port}/superset/dashboard/{dashboard}',
             self.appbuilder.get_url_for_index)[dashboard is None]
        return redirect(redirect_url)
