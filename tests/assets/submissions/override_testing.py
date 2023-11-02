class StandardMiddleware:
    def respond(self, response: str) -> str:
        return response


class Factory:
    def __init__(self, middleware) -> None:
        self.middleware = middleware

    def generate_middleware_response(self, response: str) -> str:
        return self.middleware.respond(response) + "\n" + "end$"
