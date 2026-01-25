from django.utils.deprecation import MiddlewareMixin
from utils.verify import verify_ip


class Verify_ip(MiddlewareMixin):
    EXCLUDE_PATHS = ['/account/', '/register/','/forgot_password/','/verify_code/','/reset_password/']

    def process_request(self, request):
        if request.path in self.EXCLUDE_PATHS:
            return None
        else:
            if verify_ip(request) is not True:
                return verify_ip(request)

        return None

    def process_response(self, request, response):
        return response
