from flask import request


class Webhook:
    def __init__(self, app):
        self._app = app


    def route(self, rule, secrete):
        def decorator(func):
            self._app.add_url_rule(
                rule=rule,
                endpoint='handle_webhook_request',
                view_func=lambda: self._handle_request(func, secrete),
                methods=["POST"]
            )
        return decorator


    def _handle_request(self, func, secrete):
        # TODO: Parse webhook request
        # TODO: Call func and pass data
        func("Webhook data")
        return "", 200
