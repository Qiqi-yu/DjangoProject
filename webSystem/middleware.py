from django.http import HttpResponse

class AllowOriginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'OPTIONS':
            response = HttpResponse(status=200)
        else:
            response = self.get_response(request)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Headers'] = 'Content-Type,Content-Length,Authorization,Accept,X-Requested-With'
        response['Access-Control-Allow-Methods'] = 'PUT,POST,GET,DELETE,OPTIONS'
        return response
