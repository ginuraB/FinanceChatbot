import os
import requests
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# --- Financial Data API Configuration ---
# IMPORTANT: Replace "your_alpha_vantage_api_key_here" in your .env file
# with your actual Alpha Vantage API key.
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"

def get_stock_price_from_api(symbol):
    """
    Retrieves the current stock price for a given symbol using Alpha Vantage API.
    """
    logger.info("Attempting to get real stock price for symbol: %s", symbol)
    
    if not ALPHA_VANTAGE_API_KEY:
        logger.error("ALPHA_VANTAGE_API_KEY not set in .env. Cannot fetch real stock price.")
        return {"error": "Financial data API key not configured. Please set ALPHA_VANTAGE_API_KEY in your .env file."}
    
    try:
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": ALPHA_VANTAGE_API_KEY
        }
        response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params)
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        data = response.json()

        if "Global Quote" in data:
            quote = data["Global Quote"]
            # Alpha Vantage returns strings, convert to float
            price = float(quote["05. price"])
            logger.info("Real stock price for %s: %s", symbol, price)
            return {"symbol": symbol.upper(), "price": price, "currency": "USD"}
        elif "Error Message" in data:
            error_msg = data["Error Message"]
            logger.warning("Alpha Vantage API error for %s: %s", symbol, error_msg)
            return {"error": f"Alpha Vantage API error for {symbol.upper()}: {error_msg}"}
        else:
            logger.warning("Unexpected API response for stock symbol %s: %s", symbol, data)
            return {"error": "Could not retrieve stock price for " + symbol.upper() + ". Unexpected API response."}
    except requests.exceptions.RequestException as e:
        logger.exception("Error fetching stock price from Alpha Vantage for %s:", symbol)
        return {"error": f"Failed to connect to financial data service for {symbol.upper()}: {e}"}
    except ValueError as e:
        logger.exception("Error parsing stock price data for %s:", symbol)
        return {"error": f"Failed to parse stock price data for {symbol.upper()}: {e}"}


def get_currency_exchange_rate_from_api(from_currency, to_currency):
    """
    Retrieves the current exchange rate between two currencies using Alpha Vantage API.
    """
    logger.info("Attempting to get real exchange rate from %s to %s", from_currency, to_currency)

    if not ALPHA_VANTAGE_API_KEY:
        logger.error("ALPHA_VANTAGE_API_KEY not set in .env. Cannot fetch real exchange rate.")
        return {"error": "Financial data API key not configured. Please set ALPHA_VANTAGE_API_KEY in your .env file."}

    try:
        params = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": from_currency.upper(),
            "to_currency": to_currency.upper(),
            "apikey": ALPHA_VANTAGE_API_KEY
        }
        response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if "Realtime Currency Exchange Rate" in data:
            rate_info = data["Realtime Currency Exchange Rate"]
            # Alpha Vantage returns strings, convert to float
            rate = float(rate_info["5. Exchange Rate"])
            logger.info("Real exchange rate for %s to %s: %s", from_currency, to_currency, rate)
            return {"from": from_currency.upper(), "to": to_currency.upper(), "rate": rate}
        elif "Error Message" in data:
            error_msg = data["Error Message"]
            logger.warning("Alpha Vantage API error for %s to %s: %s", from_currency, to_currency, error_msg)
            return {"error": f"Alpha Vantage API error for {from_currency.upper()} to {to_currency.upper()}: {error_msg}"}
        else:
            logger.warning("Unexpected API response for exchange rate %s to %s: %s", from_currency, to_currency, data)
            return {"error": f"Could not retrieve exchange rate for {from_currency.upper()} to {to_currency.upper()}. Unexpected API response."}
    except requests.exceptions.RequestException as e:
        logger.exception("Error fetching exchange rate from Alpha Vantage for %s to %s:", from_currency, to_currency)
        return {"error": f"Failed to connect to financial data service for {from_currency.upper()} to {to_currency.upper()}: {e}"}
    except ValueError as e:
        logger.exception("Error parsing exchange rate data for %s to %s:", from_currency, to_currency)
        return {"error": f"Failed to parse exchange rate data for {from_currency.upper()} to {to_currency.upper()}: {e}"}

