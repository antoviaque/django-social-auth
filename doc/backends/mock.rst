Mock backend
============

The mock backend allows to authenticate users through the social_auth pipeline
without making requests to a real authentication provider. This can be used for
performance testing, and to write tests for your authentication workflow.

The user is mocked by passing parameters to the auth url::

    /login/mock/?email=test@example.com&first_name=Test&last_name=Test
    /login/mock/?email=test@example.com&sleep=1000
    /login/mock/?email=test@example.com&request=http%3A%2F%2Fexample.com%2F

- "first_name", "last_name" and "fullname" allows to specify user details
  normally returned by the authentication provider.

- "sleep" will cause the backend to hang for the specified number of 
  milliseconds when a request to the authentication provider would normally 
  be initiated (performance testing)

- "request" will hit the specified remote url when a request to the
  authentication provider would normally be initiated (performance testing)

Warning! Enabling the mock backend on a production environment would be a major
security vulnerability, as it would allow anyone to authenticate as any user
without the proper credentials. To avoid this, the 
SOCIAL_AUTH_MOCK_BACKEND_ENABLED configuration variable must be set to True for 
the backend to be enabled.

