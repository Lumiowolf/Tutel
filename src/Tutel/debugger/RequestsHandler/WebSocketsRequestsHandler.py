import asyncio
import logging
import queue
import threading
from io import StringIO

import websockets
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

from Tutel.common.ErrorHandler import ErrorHandler
from Tutel.debugger.RequestsHandler.DataStructures import DebuggerResponse, DebuggerEvent, DebuggerRequest
from Tutel.debugger.RequestsHandler.RequestLexer import RequestLexer
from Tutel.debugger.RequestsHandler.RequestParser import RequestParser
from Tutel.debugger.RequestsHandler.RequestsHandlerInterface import RequestsHandlerInterface

logging.getLogger('asyncio').setLevel(logging.CRITICAL)


class WebSocketsRequestsHandler(RequestsHandlerInterface):
    _instance: "WebSocketsRequestsHandler" = None
    ACK_VALUE = "ACK"
    ack = False
    running = True
    input_queue: asyncio.Queue[str] = asyncio.Queue()
    output_queue: asyncio.Queue[str] = asyncio.Queue()
    host = ""
    port: int = 0
    request_lock = threading.Lock()

    def __init__(self, error_handler: ErrorHandler = None):
        self.error_handler = error_handler or ErrorHandler(module="debugger")
        self.error_handler.logger.disabled = True

    def start(self, request_queue: queue.Queue[tuple[DebuggerRequest, DebuggerResponse]]):
        self.request_queue = request_queue
        threading.Thread(target=self.run).start()

    def stop(self):
        WebSocketsRequestsHandler.running = False
        WebSocketsRequestsHandler.ack = True

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        start_server = websockets.serve(self.handle_client, self.host, self.port)

        loop.run_until_complete(start_server)
        try:
            loop.run_forever()
        finally:
            loop.close()

    async def handle_client(self, websocket, _):
        send_task = asyncio.create_task(self.handle_send(websocket), name="send_task")
        request_task = asyncio.create_task(self.handle_request(), name="request_task")
        receive_task = asyncio.create_task(self.handle_receive(websocket), name="receive_task")

        try:
            await asyncio.gather(send_task, request_task, receive_task)
        except ConnectionClosedError:
            pass
        except ConnectionClosedOK:
            pass
        finally:
            await websocket.close()
            await websocket.wait_closed()

            if not WebSocketsRequestsHandler.running:
                asyncio.get_event_loop().stop()

    async def handle_receive(self, websocket):
        while WebSocketsRequestsHandler.running:
            try:
                if message := await asyncio.wait_for(websocket.recv(), timeout=0.1):
                    if message == WebSocketsRequestsHandler.ACK_VALUE:
                        WebSocketsRequestsHandler.ack = True
                    else:
                        await self.input_queue.put(message)
                        self.input_queue.task_done()

            except asyncio.TimeoutError:
                pass
            await asyncio.sleep(0.1)

    async def handle_request(self):
        while WebSocketsRequestsHandler.running:
            if not self.input_queue.empty():
                raw_request = await self.input_queue.get()
                request = RequestParser(RequestLexer(StringIO(raw_request)), error_handler=self.error_handler).parse()
                response = DebuggerResponse()
                with self.request_lock:
                    self.request_queue.put((request, response))
                    while not request.finished.is_set():
                        request.finished.wait(0.1)
                        await asyncio.sleep(0.1)
                    await self.output_queue.put(response.serialize())
            await asyncio.sleep(0.1)

    async def handle_send(self, websocket):
        while not WebSocketsRequestsHandler.ack and WebSocketsRequestsHandler.running:
            await asyncio.sleep(0.1)
        while WebSocketsRequestsHandler.running:
            if not self.output_queue.empty():
                WebSocketsRequestsHandler.ack = False
                message = await self.output_queue.get()
                await websocket.send(message)
                while not WebSocketsRequestsHandler.ack:
                    await asyncio.sleep(0.1)
            await asyncio.sleep(0.1)

    def emit_event(self, event: DebuggerEvent):
        with self.request_lock:
            self.output_queue.put_nowait(event.serialize())
