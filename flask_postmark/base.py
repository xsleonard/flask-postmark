import postmark
import warnings
import logging
from flask import g

logger = logging.getLogger(__name__)


class Postmark(object):
    """
    A simple postmark loader that prefills
    mail objects with things like the api key.
    """

    def __init__(self, app=None):
        self.app = app
        if self.app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        def create_outbox():
            g.outbox = []
        self.app.before_request(create_outbox)

        if "POSTMARK_API_KEY" not in self.app.config:
            warnings.warn("POSTMARK_API_KEY not set in the configuration!")

    def get_config(self, key):
        return self.app.config.get("POSTMARK_{0}".format(key))

    def create_mail(self, *args, **kwargs):
        test_mode = kwargs.get("test_mode", None)
        if test_mode is None:
            test_mode = self.get_config("TEST_MODE")
        if test_mode:
            mail = PMTestMail(*args, **kwargs)
        else:
            mail = postmark.PMMail(*args, **kwargs)
        mail.api_key = self.get_config("API_KEY")
        if "sender" not in kwargs:
            mail.sender = self.get_config("SENDER")
        return mail


class PMTestMail(postmark.PMMail):
    def send(self, *args, **kwargs):
        kwargs["test"] = True
        sent, msg = super(PMTestMail, self).send(*args, **kwargs)
        if sent:
            g.outbox.append(msg)
        return sent, msg
