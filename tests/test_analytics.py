import pandas as pd
from app.core.analytics import execute_sql, detect_anomalies, forecast_series
from app.core.tools import tool_run_pandas_analysis, tool_data_quality, tool_dashboard


def sample():
    return pd.DataFrame({
        "region": ["East", "West", "East", "West"],
        "sales": [100, 200, 110, 10000],
        "product": ["A", "B", "A", "C"],
        "date": pd.date_range("2026-01-01", periods=4, freq="D"),
    })


def test_read_only_sql():
    result = execute_sql(sample(), 'SELECT region, SUM(sales) AS total FROM data GROUP BY region')
    assert set(result.columns) == {"region", "total"}
    assert len(result) == 2


def test_sql_rejects_mutation():
    try:
        execute_sql(sample(), "DROP TABLE data")
        assert False
    except ValueError:
        assert True


def test_anomaly_detection():
    result, rule = detect_anomalies(sample(), "sales")
    assert 10000 in result["sales"].tolist()
    assert "IQR" in rule


def test_forecast():
    result = forecast_series(sample(), "date", "sales", periods=2)
    assert len(result) == 2
    assert "forecast" in result.columns


def test_pandas_tool():
    result = tool_run_pandas_analysis(sample(), operation="groupby", group="region", metric="sales", aggregation="sum")
    assert result["row_count"] == 2


def test_quality_tool():
    result = tool_data_quality(sample())
    assert result["rows"] == 4
    assert "column_report" in result


def test_dashboard_tool():
    result = tool_dashboard(sample(), metric="sales", category="region", date_column="date")
    assert result["kpis"]["metric"] == "sales"
    assert len(result["widgets"]) >= 1
