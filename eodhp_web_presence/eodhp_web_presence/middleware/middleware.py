import environ

env = environ.Env()
IS_PROD = env("IS_PROD", default=False)


class HeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not IS_PROD:
            response["X-Robots-Tag"] = "noindex"
        return response
