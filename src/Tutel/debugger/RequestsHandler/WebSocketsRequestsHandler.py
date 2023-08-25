import asyncio
import atexit
import logging
from io import StringIO
from time import sleep

import websockets
from websockets.exceptions import ConnectionClosedError

from Tutel.common.ErrorHandler import ErrorHandler
from Tutel.debugger.RequestsHandler.DataStructures import DebuggerResponse, DebuggerEvent
from Tutel.debugger.RequestsHandler.RequestLexer import RequestLexer
from Tutel.debugger.RequestsHandler.RequestParser import RequestParser
from Tutel.debugger.RequestsHandler.RequestsHandlerInterface import RequestsHandlerInterface


logging.getLogger('asyncio').setLevel(logging.CRITICAL)


class WebSocketsRequestsHandler(RequestsHandlerInterface):
    ACK_VALUE = "ACK"
    ack = False
    running = True
    connected_clients = set()

    def __init__(self, port: int, error_handler: ErrorHandler = None):
        self.error_handler = error_handler or ErrorHandler(module="debugger")
        self.error_handler.logger.disabled = True
        self.host = ""
        self.port = port
        self.input_queue = asyncio.Queue()
        self.output_queue = asyncio.Queue()

    def start(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        start_server = websockets.serve(self.handle_client, self.host, self.port)

        loop.run_until_complete(start_server)
        try:
            loop.run_forever()
        finally:
            loop.close()

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

    async def handle_receive(self, websocket):
        while WebSocketsRequestsHandler.running:
            if message := await websocket.recv():
                if message == WebSocketsRequestsHandler.ACK_VALUE:
                    WebSocketsRequestsHandler.ack = True
                else:
                    await self.input_queue.put(message)
                    self.input_queue.task_done()
            await asyncio.sleep(0.1)

    async def handle_client(self, websocket, _):
        WebSocketsRequestsHandler.connected_clients.add(self)

        send_task = asyncio.create_task(self.handle_send(websocket), name="send_task")
        receive_task = asyncio.create_task(self.handle_receive(websocket), name="receive_task")

        try:
            await asyncio.gather(send_task, receive_task)
        except ConnectionClosedError as e:
            pass
        finally:
            await websocket.close()
            await websocket.wait_closed()
            WebSocketsRequestsHandler.connected_clients.remove(self)

            if not WebSocketsRequestsHandler.connected_clients and not WebSocketsRequestsHandler.running:
                asyncio.get_event_loop().stop()

    @classmethod
    def stop(cls):
        cls.ack = True
        cls.running = False

    def receive_request(self):
        while not self.input_queue.qsize():
            sleep(0.1)
        raw_request = self.input_queue.get_nowait()
        request = RequestParser(RequestLexer(StringIO(raw_request)), error_handler=self.error_handler).parse()
        return request

    def send_response(self, response: DebuggerResponse | DebuggerEvent):
        self.output_queue.put_nowait(response.serialize())
        self.output_queue.task_done()

atexit.register(WebSocketsRequestsHandler.stop)
