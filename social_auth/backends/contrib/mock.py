"""
Mock backend - For performance and unit testing

User is mocked by passing parameters to the auth url:
    /login/mock/?email=test@example.com&first_name=Test&last_name=Test
    /login/mock/?email=test@example.com&sleep=1000
    /login/mock/?email=test@example.com&request=http%3A%2F%2Fexample.com%2F

See the documentation for the meaning of the different varaibles.

For security reasons, the SOCIAL_AUTH_MOCK_BACKEND_ENABLED configuration variable
must be set to True for the backend to be enabled.
"""

import urllib
import urlparse
import time

from django.contrib.auth import authenticate

from social_auth.backends import OAuthBackend, BaseOAuth2, USERNAME
from social_auth.utils import setting, dsa_get


class MockOAuth2Backend(OAuthBackend):
    name = 'mock-oauth2'

    def get_user_id(self, details, response):
        return details['email']

    def get_user_details(self, response):
        email = response.get('email', '')
        return {
            USERNAME: email.split('@', 1)[0],
            'email': email,
            'fullname': response.get('fullname', ''),
            'first_name': response.get('first_name', ''),
            'last_name': response.get('last_name', '')
        }


class MockOAuth2(BaseOAuth2):
    """Mock OAuth 2"""
    AUTH_BACKEND = MockOAuth2Backend
    SETTINGS_KEY_NAME = 'MOCK_OAUTH2_CLIENT_KEY'
    SETTINGS_SECRET_NAME = 'MOCK_OAUTH2_CLIENT_SECRET'
    REDIRECT_STATE = False
    AUTHORIZATION_URL = '/oauth/callback/mock-oauth2/'

    def auth_url(self):
        """
        User is mocked by passing parameters to the auth url.

        All values desired for user are passed URL-encoded.
        """
        root_auth_url = super(MockOAuth2, self).auth_url()
        path, query_str = urllib.splitquery(root_auth_url)
        query = dict(urlparse.parse_qsl(query_str))

        for k, v in self.request.REQUEST.iteritems():
            query['mock_%s' % k] = v

        return "%s?%s" % (path, urllib.urlencode(query))

    def auth_complete(self, *args, **kwargs):
        """
        Fake out the login completion.  This would be one request.
        """
        self.validate_state()

        response = {}
        response.update(self.user_data("access_token", response))
        kwargs.update({
            'auth': self,
            'response': response,
            self.AUTH_BACKEND.name: True
        })

        return authenticate(*args, **kwargs)

    def user_data(self, access_token, *args, **kwargs):
        """
        Fake out gathering user data.  This would be another request.
        """
        # Simulate wait for HTTP request to provider in milliseconds
        req = self.request.REQUEST
        if 'mock_sleep' in req:
            time.sleep(float(req['mock_sleep']) / 1000)

        if 'mock_request' in req:
            dsa_get(req['mock_request'])

        user_data = {}
        for k, v in req.iteritems():
            if k.startswith('mock_') and not k in ('mock_sleep', 'mock_request'):
                user_data[k[5:]] = v
        return user_data

    @classmethod
    def enabled(self):
        return setting('SOCIAL_AUTH_MOCK_BACKEND_ENABLED', False)


BACKENDS = {
    'mock-oauth2': MockOAuth2
}

