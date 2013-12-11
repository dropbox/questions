from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import mail_admins
from openid.consumer.consumer import SUCCESS
from django_openid_auth.auth import OpenIDBackend


class GoogleAuthBackend(OpenIDBackend):
    def authenticate(self, **kwargs):

        openid_response = kwargs.get('openid_response')

        if openid_response is None:
            return None

        if openid_response.status != SUCCESS:
            return None

        email = openid_response.getSigned('http://openid.net/srv/ax/1.0',  'value.email')
        domain = email.split("@", 1)[1]

        if domain not in getattr(settings, "OPENID_RESTRICT_TO_DOMAINS", tuple()):
            return None

        return OpenIDBackend.authenticate(self, **kwargs)
