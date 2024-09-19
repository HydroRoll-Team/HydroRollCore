from typing import Any, Coroutine
from typing_extensions import override
from aiohttp import web, ClientWebSocketResponse

from hrc.service.utils import WebSocketService
from hrc.event import Event
from hrc.log import logger

from aiohttp import web

class WebSocketTestEvent(Event["WebSocketTestEvent"]):
    message: str
    
class WebSocketTestService(WebSocketService[WebSocketTestEvent, None]):
    name: str = "websocket_test_service"
    service_type: str = "reverse-ws"
    host: str = "127.0.0.1"
    port: int = 8765
    url: str = "/"
    
    @override
    async def handle_reverse_ws_response(self, request: web.Request) -> Coroutine[Any, Any, ClientWebSocketResponse]:
        event = WebSocketTestEvent(
            service=self,
            type="message",
            message=await request.text()
        )
        logger.info(f"Receive {event}")
        await self.handle_event(event)
        return web.Response()