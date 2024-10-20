import logging
import asyncio
import websockets


class WebSocketLogHandler(logging.Handler):
    def __init__(self, websocket_uri="ws://127.0.0.1:3002"):
        super().__init__()
        self.websocket_uri = websocket_uri
        self.loop = asyncio.get_event_loop()

    async def send_log_message(self, message):
        try:
            async with websockets.connect(self.websocket_uri) as websocket:
                await websocket.send(message)
        except Exception as e:
            print(f"Failed to send log message: {e}")

    def emit(self, record):
        log_message = self.format(record)
        # Use create_task to schedule the coroutine without blocking
        asyncio.create_task(self.send_log_message(log_message))