from typing_extensions import override

from aiohttp import web

from hrc.service.utils import HttpServerService
from hrc.event import Event
from hrc.log import logger
from aiohttp import web

class HttpServerTestEvent(Event["HttpServerTestService"]):
    """HTTP 服务端示例适配器事件类。"""

    message: str


class HttpServerTestService(HttpServerService[HttpServerTestEvent, None]):
    name: str = "http_server_service"
    get_url: str = "/"
    post_url: str = "/"
    host: str = "127.0.0.1"
    port: int = 8080


    @override
    async def handle_response(self, request: web.Request) -> web.StreamResponse:
        event = HttpServerTestEvent(
            service=self,
            type="message",
            rule="",
            message=await request.text(),
        )
        await self.handle_event(event)
        return web.Response()