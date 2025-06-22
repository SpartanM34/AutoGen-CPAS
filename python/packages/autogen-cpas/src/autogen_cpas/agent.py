from autogen_core import MessageContext, RoutedAgent, message_handler

from .models import ChatMessage
from .protocol import Role


class EchoAgent(RoutedAgent):
    """Minimal agent that echoes user content."""

    def __init__(self) -> None:
        super().__init__("Echo agent")

    @message_handler
    async def handle_message(self, message: ChatMessage, ctx: MessageContext) -> ChatMessage:
        return ChatMessage(role=Role.ASSISTANT, content=message.content)
