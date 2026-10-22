
import yfinance as yf
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os

from crew import run_financial_crew

load_dotenv()

app = FastAPI(title="AI Financial Analysis")


frontend_url = os.getenv("FRONTEND_URL")

allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

if frontend_url:
    allowed_origins.append(frontend_url.rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)



class AnalysisRequest(BaseModel):
    ticker: str = Field(min_length=1, max_length=15)


@app.get("/")
def home():
    return {
        "status": "running",
        "app": "AI Financial Analysis",
    }


def calculate_metrics(ticker: str, prices) -> dict:
    """Calculate stock metrics from a series of historical closing prices."""

    if len(prices) < 3:
        raise HTTPException(
            status_code=400,
            detail="Not enough price history to calculate metrics reliably.",
        )

    current_price = float(prices.iloc[-1])
    initial_price = float(prices.iloc[0])

    change_pct = (current_price / initial_price - 1) * 100

    returns = prices.pct_change().dropna()
    volatility = float(returns.std() * (252 ** 0.5) * 100)

    currency = "INR" if ticker.endswith((".NS", ".BO")) else "USD"

    return {
        "ticker": ticker,
        "currency": currency,
        "currency_symbol": "₹" if currency == "INR" else "$",
        "latest_close": round(current_price, 2),
        "six_month_change_pct": round(change_pct, 2),
        "annualized_historical_volatility_pct": round(volatility, 2),
        "observations": len(prices),
    }


@app.post("/analyze")
def analyze(request: AnalysisRequest):
    ticker = request.ticker.strip().upper()

    try:
        # Step 1: Fetch six months of historical stock data.
        history = yf.Ticker(ticker).history(period="6mo")

        if history.empty:
            raise HTTPException(
                status_code=404,
                detail="No market data found for this ticker.",
            )

        prices = history["Close"].dropna()
        metrics = calculate_metrics(ticker, prices)

        if len(prices) < 2:
            raise HTTPException(
                status_code=400,
                detail="Not enough price history.",
            )

        # Step 2: Calculate the financial metrics.
        current_price = float(prices.iloc[-1])
        initial_price = float(prices.iloc[0])

        change_pct = (current_price / initial_price - 1) * 100

        returns = prices.pct_change().dropna()
        volatility = float(returns.std() * (252 ** 0.5) * 100)

        currency = "INR" if ticker.endswith((".NS", ".BO")) else "USD"

        metrics = {
            "ticker": ticker,
            "currency": currency,
            "currency_symbol": "₹" if currency == "INR" else "$",
            "latest_close": round(current_price, 2),
            "six_month_change_pct": round(change_pct, 2),
            "annualized_historical_volatility_pct": round(volatility, 2),
            "observations": len(prices),
        }

        # Step 3: Run the four-agent CrewAI workflow.
        analysis = run_financial_crew(metrics)

        # Step 4: Return the results to the React frontend.
        return {
            "metrics": metrics,
            "analysis": analysis,
            "disclaimer": (
                "Educational analysis only, not financial advice. "
                "Historical performance does not predict future returns. "
                "Execution planning is simulated; no real trades are placed."
            ),
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Analysis failed: {str(exc)[:250]}",
        )
