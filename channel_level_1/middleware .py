from django.http import JsonResponse

class CustomErrorHandlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, Exception):
            return JsonResponse({'error': 'Internal Server Error. Please contact support.'}, status=500)
