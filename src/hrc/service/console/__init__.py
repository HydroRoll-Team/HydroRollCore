import asyncio
import sys
from typing_extensions import override

from hrc.event import MessageEvent
from hrc.service import Service

class ConsoleServiceEvent(MessageEvent["ConsoleService"]):
    message: str

    @override
    def get_sender_id(self) -> None:
        return None

    @override
    def get_plain_text(self) -> str:
        return self.message

    @override
    async def reply(self, message: str) -> None:
        return await self.service.send(message)

    async def is_same_sender(self) -> bool:
        return True

class ConsoleService(Service[ConsoleServiceEvent, None]):
    name: str = "console"

    @override
    async def run(self) -> None:
        while not self.core.should_exit.is_set():
            print("Please input message: ")  # noqa: T201
            message = await asyncio.get_event_loop().run_in_executor(
                None, sys.stdin.readline
            )
            await self.handle_event(
                ConsoleServiceEvent(service=self, type="message", message=message, rule="")
            )

    async def send(self, message: str) -> None:
        print(f"Send a message: {message}")  # noqa: T201