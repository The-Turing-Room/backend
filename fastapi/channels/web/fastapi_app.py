# channels/web/fastapi_app.py
import traceback

import uvicorn
from fastapi import FastAPI, Request, WebSocket, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.responses import HTMLResponse
import PyPDF2
import json

from ace.types import ChatMessage, create_chat_message
from channels.web.web_communication_channel import WebCommunicationChannel
from channels.web.web_socket_connection_manager import WebSocketConnectionManager
from media.media_replace import MediaGenerator


class FastApiApp:
    def __init__(self, ace_system, media_generators: [MediaGenerator]):
        self.app = FastAPI()
        self.ace = ace_system
        self.media_generators = media_generators
        self.admin_connection_manager = WebSocketConnectionManager()
        self.chatConnectionManager = WebSocketConnectionManager()
        self.app.add_exception_handler(Exception, self.custom_exception_handler)

        # Setup CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self.setup_routes()

    # noinspection PyUnusedLocal
    async def custom_exception_handler(self, request: Request, exc: Exception):
        """
        Custom exception handler that logs the stack trace and returns a JSON response.
        """
        print("custom_exception_handler called")
        traceback_str = traceback.format_exc()
        print(traceback_str)
        return JSONResponse(content={"error": str(exc), "traceback": traceback_str}, status_code=500)

    def setup_routes(self):
        app = self.app  # to shorten the code
        self.pdf_path = 'D:\\Downloads\\negotiation-lecture.pdf'

        @app.websocket("/ws-admin/")
        async def websocket_endpoint_admin(websocket: WebSocket):
            print("websocket_endpoint_admin called")
            await self.admin_connection_manager.connect(websocket)

        @app.websocket("/ws-chat/")
        async def websocket_endpoint_chat(websocket: WebSocket):
            print("websocket_endpoint_chat called")
            await self.chatConnectionManager.connect(websocket)

        # noinspection PyUnusedLocal
        @app.exception_handler(Exception)
        async def custom_exception_handler(request: Request, exc: Exception):
            """
            Custom exception handler that logs the stack trace and returns a JSON response.
            """
            traceback_str = traceback.format_exc()
            print(traceback_str)
            return JSONResponse(content={"error": str(exc), "traceback": traceback_str}, status_code=500)

        @app.post("/chat/")
        async def chat(request: Request):
            if self.pdf_path is None:
                raise HTTPException(status_code=400, detail="Please upload a pdf")

            data = await request.json()
            messages: str = data.get('messages', '')
            slide_number: int = int(data.get('slide_number', None))

            # Ensure slide_number is provided
            if slide_number is None:
                raise HTTPException(status_code=400, detail="Slide number is required")

            # Read the PDF file and extract text
            full_text = ""
            slide_text = ""
            try:
                with open(self.pdf_path, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    # Extract the full text content
                    for page in pdf_reader.pages:
                        full_text += page.extract_text() + "\n"

                    # Extract text from the specified slide
                    slide_text = pdf_reader.pages[slide_number - 1].extract_text()
            except Exception as e:
                print("Error occurred while reading the PDF file!")
                traceback_str = traceback.format_exc()
                print(traceback_str)
                return JSONResponse(content={"error": str(e), "traceback": traceback_str}, status_code=500)

            # Construct the system prompt
            system_prompt = f"TEXTUAL LECTURE CONTENT:\n{full_text}\n\nCONTENT ON SLIDE {slide_number}:\n=======================\n\n{slide_text}"

            # Include conversation history in the prompt
            # Assuming messages is a list of ChatMessage objects and contains the conversation history
            # conversation_history = "\n".join([f"{msg.sender}: {msg.text}" for msg in messages])
            final_prompt = f"{system_prompt}\n\nConversation History:\n{messages}"

            # Process the message
            try:
                result = await self.ace.l3_agent.process_incoming_user_message(final_prompt)
                result = result.replace('\n', '\\n')
                return JSONResponse(content={"success": True, "content": json.loads(result)[0]}, status_code=200)
            except Exception as e:
                print("Error occurred while processing incoming user message!")
                traceback_str = traceback.format_exc()
                print(traceback_str)
                return JSONResponse(content={"error": str(e), "traceback": traceback_str}, status_code=500)


        @app.post("/publish_pdf/")
        async def publish_pdf(request: Request):
            data = await request.json()
            print(f'GOT DATA: {data}')
            file_path= data['file_path']
            self.pdf_path = file_path
            try:
                # Assuming the file_path is a path to a file on the server
                # Validate file_path here if necessary
                with open(file_path, 'rb') as original_file, open('lecture.pdf', 'wb') as new_file:
                    new_file.write(original_file.read())
                return {"success": True, "message": "PDF saved as 'lecture.pdf'"}
            except Exception as e:
                print("Error occurred while saving the PDF file!")
                traceback_str = traceback.format_exc()
                print(traceback_str)
                return JSONResponse(content={"error": str(e), "traceback": traceback_str}, status_code=500)


        @app.get("/chat/")
        async def chat_get(message: str):
            """
            For testing purposes. Lets you send a single chat message and see the response (if any)
            """
            if not message:
                raise HTTPException(status_code=400, detail="message parameter is required")
            messages = [create_chat_message("api-user", message)]
            communication_channel = WebCommunicationChannel(messages, self.chatConnectionManager, self.media_generators)

            try:
                await self.ace.l3_agent.process_incoming_user_message(communication_channel)
                return "Message sent to Stacey"
            except Exception as e:
                traceback_str = traceback.format_exc()
                print(traceback_str)
                return JSONResponse(content={"error": str(e), "traceback": traceback_str}, status_code=400)

        @app.get("/bus/")
        async def view_bus(name: str):
            if name == 'northbound':
                return self.ace.northbound_bus.messages()
            elif name == 'southbound':
                return self.ace.southbound_bus.messages()
            else:
                raise HTTPException(status_code=400, detail="Invalid bus name. Choose 'northbound' or 'southbound'.")

        @app.post("/publish_message/")
        async def publish_message(request: Request):
            print("publish_message called")
            data = await request.json()
            print("data: " + str(data))
            sender = data.get('sender')
            message = data.get('message')
            bus_name = data.get('bus')

            if not sender or not message or not bus_name:
                print("sender, message, and bus are required fields")
                raise HTTPException(status_code=400, detail="sender, message, and bus are required fields")

            if bus_name == 'northbound':
                bus = self.ace.northbound_bus
            elif bus_name == 'southbound':
                bus = self.ace.southbound_bus
            else:
                raise HTTPException(status_code=400, detail="Invalid bus name. Choose 'northbound' or 'southbound'.")

            await bus.publish(sender, message)
            return {"success": True, "message": "Message published successfully"}

        @app.post("/clear_messages/")
        async def clear_messages(request: Request):
            data = await request.json()
            bus_name = data.get('bus')
            if not bus_name:
                raise HTTPException(status_code=400, detail="'bus' is a required field")

            if bus_name == 'northbound':
                bus = self.ace.northbound_bus
            elif bus_name == 'southbound':
                bus = self.ace.southbound_bus
            else:
                raise HTTPException(status_code=400, detail="Invalid bus name. Choose 'northbound' or 'southbound'.")

            bus.clear_messages()
            return {"success": True, "message": "Messages cleared successfully"}

        @app.get("/", response_class=HTMLResponse)
        def root():
            return ('<html>Hi! Stacey here. Yes, the backend is up and running! '
                    '<a href="chat?message=hi">/chat?message=hi</a></html>')

    def setup_listeners(self):
        for bus in [self.ace.northbound_bus, self.ace.southbound_bus]:
            bus.subscribe(self.create_bus_listener(bus))

        for layer in self.ace.get_layers():
            layer.add_status_listener(self.create_layer_status_listener(layer))

    def create_bus_listener(self, bus):
        async def listener(sender, message):
            try:
                print(f"flask_app detected message on bus from {sender}: {message}")
                await self.admin_connection_manager.send_message({
                    'eventType': 'busMessage',
                    'data': {
                        'bus': bus.name,
                        'sender': sender,
                        'message': message
                    }
                })
            except Exception as e:
                print(f"Error in bus listener: {e}")
        return listener

    def create_layer_status_listener(self, layer):
        async def listener(status):
            try:
                print(f"flask_app detected status change in layer {layer.get_id}: {status}")
                await self.admin_connection_manager.send_message({
                        'eventType': 'layerStatus',
                        'data': {
                            'layerId': layer.get_id(),
                            'status': status.name
                        }
                })
            except Exception as e:
                print(f"Error in layer status listener: {e}")
        return listener

    async def run(self):
        self.setup_listeners()
        config = uvicorn.Config(app=self.app, host="localhost", port=5000)
        server = uvicorn.Server(config)
        return await server.serve()
