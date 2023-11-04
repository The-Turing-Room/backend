from ace.ace_system import AceSystem
from llm.gpt import GPT
from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel


load_dotenv(find_dotenv())

app = FastAPI()

# Initialize the components required for the AceSystem
llm = GPT('')
ace_system = AceSystem(llm, "claude-2")

class ChatRequest(BaseModel):
    conversation_history: str
    slide_number: int

@app.on_event("startup")
async def startup_event():
    # Start the AceSystem
    await ace_system.start()

@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        with open("lecture.pdf", "wb") as buffer:
            buffer.write(file.file.read())
        return {"message": "File uploaded successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/")
async def chat(chat_request: ChatRequest):
    try:
        # Assume `AceSystem` has been instantiated with `ace`
        # and it has a `respond` method that processes the message
        slide_number = chat_request.slide_number
        response = await ace_system.l3_agent.process_incoming_user_message(chat_request.conversation_history)
        return JSONResponse(content={"response": response})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the server with `uvicorn main:app --reload`
