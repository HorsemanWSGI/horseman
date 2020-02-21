import base64
import wrapt
from horseman.response import Response
from inspect import isfunction, ismethod
from functools import wraps


unauthorized = Response.create(401)


def authenticate(checkers, unauthorized=unauthorized, **conf):

    @wrapt.decorator
    def authenticator(wrapped, instance, args, kwargs):
        request = args[0]
        auth = request.environ.get('HTTP_AUTHORIZATION')
        if auth is not None:
            authtype, authvalue = auth.split(' ', 1)
            checker = checkers.get(authtype.lower())
            if checker is not None:
                code, payload = checker(
                    authvalue, request.environ, conf)

                if code == 200:
                    request.environ['auth_payload'] = payload
                    return wrapped(*args)

        return unauthorized

    return authenticator


class BasicAuth:

    def __init__(self, realm, users, session_key=None):
        self.realm = realm
        self.session_key = session_key
        self.users = users

    @property
    def unauthorized(self):
        return Response.create(401, headers={
            'WWW-Authenticate':
            f'Basic realm="{self.realm}", charset="UTF-8"'
        })

    def valid_user(self, username, password):
        if username in self.users:
            if self.users[username] == password:
                return True
        return False

    def session_dict(self, environ):
        """Get the session for caching username.
        """
        if self.session_key is None:
            return None
        return environ.get(self.session_key)

    def save_session(self, environ):
        """Save out the session.
        Replace with a do-nothing if you use a package that does
        not require you to explicitly save out sessions.
        """
        session = self.session_dict(environ)
        if session is not None:
            return session.save()

    def cache_username(self, environ, username):
        """Store the username in a session dict if found.

        Also populates REMOTE_USER.
        """
        environ['REMOTE_USER'] = username
        session = self.session_dict(environ)
        if session is not None:
            session[self.session_user_key] = username

    def get_cached_username(self, environ):
        """Look for the username in the session if found.

        Also populates REMOTE_USER if it can.
        """
        session = self.session_dict(environ)
        if session is not None:
            return session.get(self.session_user_key)
        else:
            return None

    def username_and_password(self, authvalue):
        auth = base64.b64decode(authvalue)
        if isinstance(auth, bytes):
            auth = auth.decode()
        return auth.split(':')

    def __call__(self, authvalue, environ, conf):
        username, password = self.username_and_password(authvalue)
        if username and password:
            if self.valid_user(username, password):
                self.cache_username(environ, username)
                return 200, None
        else:
            username = self.get_cached_username(environ)
            if username is not None:
                self.cache_username(environ, username)
                return 200, None
        return 403, None
