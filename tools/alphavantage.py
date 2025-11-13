# tools/alphavantage.py
import requests
from langchain_core.tools import tool
from typing import Dict, Any, List
import json
from settings import get_settings

SETTINGS = get_settings()

def call_alphavantage_api(params: Dict[str,Any]):
    """Internal Helper function to call Alpha Vantage API and common error checks"""
    params["apikey"] = SETTINGS.alphavantage_api_key


    try:
        response = requests.get(SETTINGS.alphavantage_base_url,params = params,timeout=15)
        response.raise_for_status()
        data = Dict[str,Any] = response.json()

        # Checks for AV specific error messages (i.e invalid symbol, rate limits)
        if "Error Message" in data:
            raise ValueError(f"Alpha Vantage API Error: {data['Error Message']}")
        if "Note" in data:
            #This would indicate rate limiting or data unavailability for free tiers
            raise ValueError(f"Alpha Vantage API Notice: {data['Note']}")
        
        return data
    

    except requests.exceptions.HTTPError as e:
        return {"Error": f"HTTP Error: Could not reach AlphaVantage. Check API key and service status. ({e})"}
    except requests.exceptions.RequestException as e:
        return {"Error": f"Network/Connection Error: {e}"}
    except ValueError as e:
        return {"Error": f"API returned an error: {e}"}
    except Exception as e:
        return {"Error": f"An unexpected error occurred: {e}"}
    



@tool
def search_symbol(keywords:str):
 """
    Utility tool to search for a stock ticker symbol based on company name keywords. 
    Always use this tool first if the user provides a company name instead of a ticker.
    Example Input: 'search_symbol(keywords="Alphabet Inc")'

    """
 
 params = {"function":"SYMBOL_SEARCH","keywords":keywords}
 data = call_alphavantage_api(params)

 if "Error" in data:
     return data["Error"]
 
 best_match = data.get("bestMatches",[])

 if not best_match:
     return f"No matching symbols found for keywords: {keywords}"
 
 first_match = best_match[0]


 symbol = first_match.get("1. symbol")
 name = first_match.get("2. name")

 return f"Best match for '{keywords}': Symbol: {symbol}, Name: {name}"


@tool
def get_stock_price(symbol: str):
    """
    Fetches the latest intraday stock price and volume for the given ticker symbol (e.g, AAPL)
    Use this for quick " What is the price of X?" queries.
    """

    params = {"function":"GLOBAL_QUOTE","symbol":symbol.upper()}
    data = call_alphavantage_api(params)


    if "Error" in data or "Note" in data:
        return data.get("Error") or data.get("Note", f"Data not found for symbol {symbol}.")
    
    quote = data.get("Global Quote",{})

    if not quote or 'price' not in quote:
        return f"No price data found for symbol: {symbol}"
    
    price = quote.get('05. price')
    volume = quote.get('06. volume')
    
    return f"The latest stock price for {symbol.upper()} is **${price}**. Volume: {int(volume):,}."




@tool
def get_historical_sma(symbol: str, interval: str = "daily", time_period: int = 50) -> str:
    """
    Calculates the Simple Moving Average (SMA) technical indicator for a given stock symbol.
    Use this for trend/momentum queries like 'What is the 50-day moving average for TSLA?'.
    Valid intervals are 'daily', 'weekly', or 'monthly'. Time period is the number of data points.
    """
    function_map = {
        "daily": "SMA",
        "weekly": "SMA",
        "monthly": "SMA"
    }
    
    if interval not in function_map:
        return f"Error: Invalid interval '{interval}'. Choose from 'daily', 'weekly', or 'monthly'."

    params = {
        "function": function_map[interval],
        "symbol": symbol.upper(),
        "interval": "daily" if interval == "daily" else "None", # AlphaVantage parameter quirk
        "time_period": time_period,
        "series_type": "close",
    }
    
    data = call_alphavantage_api(params)
    
    if "Error" in data or "Note" in data:
        return data.get("Error") or data.get("Note", f"Technical indicator data not found for {symbol}.")
        
    # The key is dynamic (e.g., 'Technical Analysis: SMA')
    indicator_data = next((v for k, v in data.items() if 'Technical Analysis' in k), None)
    
    if not indicator_data:
        return f"Failed to parse SMA data for {symbol}. Raw response keys: {list(data.keys())}."
        
    # Get the latest date's value
    latest_date = next(iter(indicator_data))
    latest_value = indicator_data[latest_date].get("SMA")
    
    return (
        f"The latest {time_period}-{interval} Simple Moving Average (SMA) for {symbol.upper()} "
        f"as of {latest_date} is **${latest_value}**."
    )

@tool
def get_income_statement(symbol: str):
     """
     Fetches the annual income statement of a company, focusing on key metrics.
     Use this for fundamental analysis queries like 'what was apple's revenue last year?'
     """

     params = {"function":"INCOME_STATEMENT","symbol":symbol.upper()}
     data = call_alphavantage_api(params)


     if "Error" in data or "Note" in data:
        return data.get("Error") or data.get("Note", f"Data not found for symbol {symbol}.")
     
     annual_reports = data.get("annualReports",[])

     if not annual_reports: 
         return f"Could not find income statement data for symbol: {symbol}"
     
     latest_report = annual_reports[0]

     fiscal_date = latest_report.get("fiscalDateEnding")
     revenue = latest_report.get("totalRevenue")
     net_income = latest_report.get("netIncome")

     def format_money(value):
         try:
             val = int(value)
             return f"${val / 1_000_000_000:.2f} Billion"
         except (ValueError, TypeError):
             return "N/A"
         
     return(
        f"Latest Annual Income Statement for {symbol.upper()} (Fiscal Year End: {fiscal_date}):\n"
        f"* Total Revenue: **{format_money(revenue)}**\n"
        f"* Net Income: **{format_money(net_income)}**"
         )

# The comprehensive list of all tools available to the LangChain Agent
FINANCIAL_TOOLS = [search_symbol, get_stock_price, get_historical_sma, get_income_statement]




     



    

        
