import functools
import logging
from flask import session

import jwt
from flask import request
from flask_login import login_user, logout_user

from superset.reports.models import ReportRecipientType

logger = logging.getLogger(__name__)


def impersonate(username: str):
    def _impersonate(f):
        def wraps(self, *args, **kwargs):
            token = request.args.get('token')
            if token is None:
                return self.response_401()
            logger.info(f'token = {token}')
            try:
                decoded = jwt.decode(token, options={"verify_signature": False})
            except:
                return self.response_401()
            logger.info(f'decoded = {decoded}')
            user = self.appbuilder.sm.find_user(username=username)
            logout_user()
            login_user(user, remember=False)
            for key in decoded:
                session[key] = decoded[key]
            logger.info(f'session = {session}')
            return f(self, *args, **kwargs)

        return functools.update_wrapper(wraps, f)

    return _impersonate
