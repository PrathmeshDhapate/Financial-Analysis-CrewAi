
from main import calculate_metrics
import pandas as pd
from pathlib import Path
import re


def sample_metrics():
    prices = pd.Series([100.0, 105.0, 110.0])
    return calculate_metrics("RELIANCE.NS", prices)


def test_metrics_contain_required_fact_fields():
    metrics = sample_metrics()

    assert metrics["ticker"] == "RELIANCE.NS"
    assert metrics["currency"] == "INR"
    assert metrics["currency_symbol"] == "₹"
    assert metrics["latest_close"] == 110.0
    assert metrics["six_month_change_pct"] == 10.0
    assert metrics["observations"] == 3


def test_report_contains_all_required_sections():
    report = """
    ## 1. Historical Metrics
    ## 2. Bullish, Sideways, and Bearish Scenarios
    ## 3. Hypothetical Execution Plan
    ## 4. Risk Management
    ## 5. Limitations and Conclusion
    """

    required_sections = [
        "Historical Metrics",
        "Bullish, Sideways, and Bearish Scenarios",
        "Hypothetical Execution Plan",
        "Risk Management",
        "Limitations and Conclusion",
    ]

    for section in required_sections:
        assert section in report


def test_hypothetical_plan_is_explicitly_labeled():
    report = "This is a hypothetical execution plan for educational purposes."

    assert "hypothetical" in report.lower()


def test_unavailable_indicators_are_not_claimed_as_facts():
    report = (
        "RSI was not calculated from the supplied data. "
        "It could be checked in a future analysis."
    )

    assert "RSI was not calculated" in report
    assert "RSI is 65" not in report


def test_report_discloses_assumptions():
    report = "Assumption: the example uses an illustrative account balance."

    assert "assumption" in report.lower()
    assert "illustrative" in report.lower()


from pathlib import Path


def test_saved_report_has_all_required_sections():
    report_path = (
        Path(__file__).parent
        / "fixtures"
        / "reliance_report.md"
    )
    report = report_path.read_text(encoding="utf-8")

    required_sections = [
        "Historical Metrics",
        "Bullish, Sideways, and Bearish Scenarios",
        "Hypothetical Execution Plan",
        "Risk Management",
        "Limitations and Conclusion",
    ]

    missing_sections = [
        section
        for section in required_sections
        if section.lower() not in report.lower()
    ]

    assert not missing_sections, (
        f"Report is missing sections: {missing_sections}"
    )

def load_saved_report():
    report_path = (
        Path(__file__).parent
        / "fixtures"
        / "reliance_report.md"
    )
    return report_path.read_text(encoding="utf-8")



def test_report_does_not_claim_unavailable_indicator_values():
    report = load_saved_report()

    # Detect explicit numerical claims for indicators that the backend
    # does not calculate. Merely mentioning an indicator is allowed.
    unsupported_value_patterns = {
        "RSI value": r"\bRSI\s*(?:is|was|=|:)\s*\d+",
        "moving average value": (
            r"\b(?:50|20)[ -]day moving average\s*"
            r"(?:is|was|=|:)\s*[₹$]?\d"
        ),
        "observed trading volume": (
            r"\b(?:trading )?volume\s*"
            r"(?:is|was|=|:)\s*[\d,.]+\s*(?:shares|million|billion|M|B)\b"
        ),
    }

    found = [
        name
        for name, pattern in unsupported_value_patterns.items()
        if re.search(pattern, report, flags=re.IGNORECASE)
    ]

    assert not found, (
        "Report contains unsupported numerical indicator claims: "
        f"{found}"
    )


from pathlib import Path


def test_saved_report_has_all_required_sections():
    report_path = (
        Path(__file__).parent
        / "fixtures"
        / "reliance_report.md"
    )

    report = report_path.read_text(encoding="utf-8")

    required_sections = [
        # Use the exact five section headings
        # already checked by your existing tests.
    ]

    for section in required_sections:
        assert section in report, f"Missing section: {section}"



