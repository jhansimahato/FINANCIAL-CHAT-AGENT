# settings.py
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Configuration loaded from environment variables/dotenv."""
    
    # Configure the source of environment variables
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    # LLM Settings
    llm_api_key: str = Field(..., env='LLM_API_KEY')
    llm_model_name: str = "gpt-4" # Default or use env var

    # AlphaVantage Settings
    alphavantage_api_key: str = Field(..., env='ALPHAVANTAGE_API_KEY')
    alphavantage_base_url: str = "https://www.alphavantage.co/query"
    
    # System Prompt for the Agent
    system_message: str = (
        "You are an expert financial and stock market analyst. "
        "Your role is to interpret user queries about stock data, execute the AlphaVantage tools to fetch the data, and summarize the results clearly. "
        "Always rely on the provided tools if the query is finance-related. If a tool call fails or no tool is relevant, state clearly that you cannot fulfill the request."
    )

def get_settings() -> Settings:
    """Dependency function to get application settings."""
    return Settings()