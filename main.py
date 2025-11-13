# main.py
from fastapi import FastAPI
from Router.chat_router import router as chat_router
from settings import get_settings
import uvicorn

# Initialize settings once to ensure environment variables are loaded
SETTINGS = get_settings()

app = FastAPI(
    title="GenAI Financial Chat Service",
    description="A modular conversational agent powered by LangChain and AlphaVantage data."
)

# Attach the modular API routes
app.include_router(chat_router)

if __name__ == "__main__":
    print("Starting FastAPI service. Go to http://127.0.0.1:8000/docs for Swagger UI.")
    uvicorn.run(app, host="0.0.0.0", port=8000)
    