from drfasyncview import AsyncAPIView
from django.http import HttpRequest
from django.http import HttpResponse
from utils import LogSystem
from .configure import LOG_PATH
from .configure import DEBUG
import logging


class HealthCheck(AsyncAPIView):
    logger = LogSystem(
        module_name=__name__,
        log_path=LOG_PATH,
        log_level=logging.DEBUG if DEBUG else logging.INFO
    )

    @logger.log(log_level=logging.DEBUG)
    async def get(
        self,
        request: HttpRequest,
    ) -> HttpResponse:
        return HttpResponse("Healthcheck OK")

    @logger.log(log_level=logging.DEBUG)
    async def post(
        self,
        request: HttpRequest,
    ) -> HttpResponse:
        return HttpResponse("Healthcheck OK")
