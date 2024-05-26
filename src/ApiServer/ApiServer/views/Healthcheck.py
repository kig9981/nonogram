from drfasyncview import AsyncAPIView
from django.http import HttpRequest
from django.http import HttpResponse


class HealthCheck(AsyncAPIView):
    async def get(
        self,
        request: HttpRequest,
    ) -> HttpResponse:
        return HttpResponse("Healthcheck OK")

    async def post(
        self,
        request: HttpRequest,
    ) -> HttpResponse:
        return HttpResponse("Healthcheck OK")
