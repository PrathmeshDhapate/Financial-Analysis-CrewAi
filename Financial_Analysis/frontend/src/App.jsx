
import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "./App.css";

const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function App() {
  const [ticker, setTicker] = useState("AAPL");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function analyzeStock(e) {
    e.preventDefault();

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ticker: ticker.trim().toUpperCase(),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Analysis failed.");
      }

      setResult(data);
    } catch (err) {
      setError(
        err.message || "Could not connect to the backend."
      );
    } finally {
      setLoading(false);
    }
  }

  const metrics = result?.metrics;

  // Normalize escaped Markdown characters returned by the AI.
  const normalizedAnalysis = result?.analysis
    ? result.analysis
        .replace(/\\\|/g, "|")
        .replace(/\\#/g, "#")
        .replace(/\\\*/g, "*")
        .replace(/\\`/g, "`")
        .replace(/\\\s*$/gm, "")
    : "";

  return (
    <main className="container">
      <header className="header">
        <div className="brand">
          FIN<span>INSIGHT</span>
        </div>

        <span className="status">
          <i /> AI ANALYSIS
        </span>
      </header>

      <section className="hero">
        <p className="eyebrow">AI-POWERED MARKET RESEARCH</p>

        <h1>
          Understand the market.
          <br />
          <span>Think more clearly.</span>
        </h1>

        <p className="subtitle">
          Explore historical stock performance, volatility, and
          AI-generated financial insights in one place.
        </p>

        <form className="search" onSubmit={analyzeStock}>
          <label htmlFor="ticker">STOCK SYMBOL</label>

          <div className="search-row">
            <input
              id="ticker"
              value={ticker}
              onChange={(e) => setTicker(e.target.value)}
              placeholder="e.g. AAPL"
              maxLength={15}
              required
            />

            <button type="submit" disabled={loading}>
              {loading ? "Analyzing..." : "Analyze stock ↗"}
            </button>
          </div>
        </form>
      </section>

      {loading && (
        <div className="notice">
          Fetching market data and generating your report...
        </div>
      )}

      {error && <div className="error">{error}</div>}

      {metrics && (
        <>
          <section className="section-heading">
            <div>
              <p className="eyebrow">MARKET OVERVIEW</p>
              <h2>
                {metrics.ticker}{" "}
                <span>· Six-month analysis</span>
              </h2>
            </div>

            <span className="live-label">Historical data</span>
          </section>

          <section className="metrics">
            <article className="metric-card">
              <p>Latest closing price</p>
              <h3>
                {metrics.currency_symbol || "$"}
                {Number(metrics.latest_close).toLocaleString(
                  metrics.currency === "INR" ? "en-IN" : "en-US",
                  {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  }
                )}
              </h3>
            </article>

            <article className="metric-card">
              <p>Six-month change</p>
              <h3
                className={
                  metrics.six_month_change_pct >= 0
                    ? "positive"
                    : "negative"
                }
              >
                {metrics.six_month_change_pct > 0 ? "+" : ""}
                {metrics.six_month_change_pct}%
              </h3>
            </article>

            <article className="metric-card">
              <p>Annualized volatility</p>
              <h3>
                {metrics.annualized_historical_volatility_pct}%
              </h3>
            </article>

            <article className="metric-card">
              <p>Trading observations</p>
              <h3>{metrics.observations}</h3>
            </article>
          </section>

          <section className="report">
            <div className="report-title">
              <div>
                <p className="eyebrow">YOUR GENERATED REPORT</p>
                <h2>Financial analysis</h2>
              </div>

              <span className="ai-badge">
                ✦ AI GENERATED
              </span>
            </div>

            <div className="analysis">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  table: ({ children }) => (
                    <div className="table-wrapper">
                      <table>{children}</table>
                    </div>
                  ),
                }}
              >
                {normalizedAnalysis}
              </ReactMarkdown>
            </div>

            <p className="disclaimer">{result.disclaimer}</p>
          </section>
        </>
      )}

      {!result && !loading && !error && (
        <section className="empty">
          <div className="empty-icon">↗</div>
          <h2>Your next analysis starts here</h2>
          <p>
            Enter a ticker above to explore its historical
            performance and risks.
          </p>
        </section>
      )}

      <footer>
        FININSIGHT · Educational project · Not financial advice
      </footer>
    </main>
  );
}

export default App;
