
import os

from crewai import Agent, Crew, Process, Task, LLM


def run_financial_crew(metrics: dict) -> str:
    """
    Run a four-agent financial analysis workflow.
    No real trades are placed.
    """

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing from .env")

    
    
    llm = LLM(
        model="openai/openai/gpt-oss-20b",
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
        custom_openai=True,
        temperature=0.3,
        max_tokens=3000,
    )



    data_analyst = Agent(
        role="Financial Data Analyst",
        goal="Explain the supplied historical stock metrics accurately.",
        backstory=(
            "You specialize in interpreting historical stock prices, "
            "percentage changes, and annualized volatility. "
            "Never invent data that was not supplied."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

    strategy_developer = Agent(
        role="Trading Strategy Developer",
        goal="Develop hypothetical scenarios based on the historical analysis.",
        backstory=(
            "You examine historical performance and develop conditional "
            "scenarios. You distinguish observations from speculation and "
            "never guarantee returns."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

    execution_planner = Agent(
        role="Trade Execution Planner",
        goal="Create a hypothetical execution plan without placing trades.",
        backstory=(
            "You plan simulated trade execution, considering entry conditions, "
            "position sizing, liquidity, and order types. You never connect "
            "to a brokerage or submit real orders."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

    risk_manager = Agent(
        role="Risk Management Analyst",
        goal="Assess the risks and produce a balanced final report.",
        backstory=(
            "You evaluate volatility, uncertainty, downside scenarios, and "
            "limitations. You ensure the report does not present hypothetical "
            "scenarios as predictions or personalized financial advice."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

    analyze_data = Task(
        description=(
            "Analyze the following historical metrics for {ticker}:\n"
            "{metrics}\n\n"
            "Explain the six-month price change, latest close, annualized "
            "historical volatility, and observation count. Use only the "
            "provided figures. Clearly state that these are historical data.\n\n"
            "Use the currency specified in the metrics for all prices and "
            "financial calculations. Never assume USD when the currency is INR. "
            "Keep hypothetical account sizes and trade examples in the same "
            "currency, and label them as illustrative assumptions."
        ),
        expected_output=(
            "A concise analysis of the supplied metrics, including their "
            "meaning and limitations."
        ),
        agent=data_analyst,
    )

    develop_strategy = Task(
        description=(
            "Using the historical metrics and data analyst's findings, "
            "describe bullish, sideways, and bearish hypothetical scenarios. "
            "For each scenario, explain possible drivers and what evidence "
            "would support it. Do not invent current news or price targets."
        ),
        expected_output=(
            "A balanced scenario analysis with assumptions clearly identified."
        ),
        agent=strategy_developer,
        context=[analyze_data],
    )

    plan_execution = Task(
        description=(
            "Create an educational, hypothetical execution plan based on the "
            "previous analysis. Discuss what a simulated entry condition, "
            "position sizing, and risk limit might involve. Do not prescribe "
            "a personalized trade, invent a live price, or place any order."
        ),
        expected_output=(
            "A simulated execution plan, its assumptions, and a clear "
            "statement that no real trade was executed."
        ),
        agent=execution_planner,
        context=[analyze_data, develop_strategy],
    )

    assess_risk = Task(
        description=(
            "Produce the FINAL financial analysis report for {ticker} in Markdown.\n\n"
            "Include these sections in this exact order:\n"
            "1. Historical Metrics\n"
            "2. Bullish, Sideways, and Bearish Scenarios\n"
            "3. Hypothetical Execution Plan\n"
            "4. Risk Management\n"
            "5. Limitations and Conclusion\n\n"
            "Use the supplied historical metrics and the preceding task outputs.\n"
            "Never invent or imply that you calculated RSI, SMA, ATR, trading "
            "volume, implied volatility, current news, or other indicators that "
            "were not supplied or actually calculated.\n"
            "If an indicator is useful, label it as a hypothetical condition to "
            "check, not as a verified current value.\n\n"
            "Any execution plan must be explicitly hypothetical. Keep account "
            "size, position size, entry price, stop-loss, and maximum loss "
            "mathematically consistent. Do not claim an order was placed.\n"
            "Distinguish historical facts, assumptions, and possible scenarios.\n"
            "Keep the report informative but concise. Finish all five sections "
            "and include a clear conclusion. Do not stop after the execution plan."
        ),
        expected_output=(
            "A complete Markdown report with all five requested sections, "
            "grounded historical metrics, clearly labeled hypothetical scenarios, "
            "consistent illustrative risk calculations, and limitations."
        ),
        agent=risk_manager,
        context=[analyze_data, develop_strategy, plan_execution],
    )

    crew = Crew(
        agents=[
            data_analyst,
            strategy_developer,
            execution_planner,
            risk_manager,
        ],
        tasks=[
            analyze_data,
            develop_strategy,
            plan_execution,
            assess_risk,
        ],
        process=Process.sequential,
        verbose=False,
    )

    result = crew.kickoff(
        inputs={
            "ticker": metrics["ticker"],
            "metrics": str(metrics),
        }
    )

    return str(result)
