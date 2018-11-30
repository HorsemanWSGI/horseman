class authenticate:

    def __init__(self, checkers, **conf):
        self.checkers = checkers
        self.conf = conf

    def __call__(self, app):
        def method_watchdog(environ, start_response):
            auth = environ.get('HTTP_AUTHORIZATION')
            if auth is not None:
                authtype, authvalue = auth.split(' ', 1)
                checker = self.checkers.get(authtype)
                if checker is not None:
                    code, payload = self.checker(
                        authvalue, environ, self.conf)

                    if code == 200:
                        environ['auth_payload'] = payload
                        return app(environ, start_response)
                    else:
                        return reply(code, text=payload)(
                            environ, start_response)
            return reply(401)(environ, start_response)
        return method_watchdog
