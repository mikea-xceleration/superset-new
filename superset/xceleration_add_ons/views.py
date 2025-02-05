import traceback
import uuid
from typing import Any

from flask import request
from flask_appbuilder import expose
from flask_appbuilder.security.views import AuthDBView

import logging

logger = logging.getLogger(__name__)


class StandardAuthDbView(AuthDBView):
    @expose('/login/', methods=['GET', 'POST'])
    def login(self) -> Any:
        request_id = str(uuid.uuid4())
        logger.info(
            "Processing standard login request: "
            f"request_id={request_id}, "
            f"user_agent={request.user_agent.string}, "
            f"remote_addr={request.remote_addr}"
        )
        try:
            result = super().login()
            logger.info(
                f"Standard login result: "
                f"request_id={request_id}, "
                "success=True"
            )
            return result
        except Exception as e:
            logger.error(
                f"Error during standard login: "
                f"request_id={request_id}, "
                f"error={str(e)}, "
                f"traceback={traceback.format_exc()}"
            )
            raise
