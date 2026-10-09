import re
import numpy as np
import pandas as pd
import duckdb
import plotly.express as px


def safe_identifier(name):
    return '"' + str(name).replace('"', '""') + '"'


def register_dataframe(df):
    con = duckdb.connect(database=":memory:")
    con.register("data", df)
    return con


def execute_sql(df, sql):
    cleaned = sql.strip().rstrip(";")
    if not re.match(r"^(select|with)\b", cleaned, flags=re.I):
        raise ValueError("Only read-only SELECT/WITH SQL is allowed.")
    if re.search(r"\b(insert|update|delete|drop|alter|create|copy|attach|detach|install|load|call)\b", cleaned, flags=re.I):
        raise ValueError("Potentially mutating or external SQL was rejected.")
    con = register_dataframe(df)
    try:
        return con.execute(cleaned).df()
    finally:
        con.close()


def detect_anomalies(df, numeric_col=None, method="iqr"):
    numeric = df.select_dtypes(include="number").columns.tolist()
    if numeric_col is None:
        if not numeric:
            return pd.DataFrame(), "No numeric columns available."
        numeric_col = numeric[0]
    if numeric_col not in df.columns:
        raise ValueError(f"Unknown numeric column: {numeric_col}")
    s = pd.to_numeric(df[numeric_col], errors="coerce")
    valid = s.dropna()
    if valid.empty:
        return pd.DataFrame(), f"No usable numeric values in {numeric_col}."
    if method == "zscore":
        std = valid.std(ddof=0)
        if std == 0:
            mask = pd.Series(False, index=df.index)
            rule = "z-score method with zero standard deviation; no values can be flagged."
        else:
            z = (s - valid.mean()) / std
            mask = z.abs() >= 3
            rule = f"Absolute z-score >= 3; mean={valid.mean():.4f}, population std={std:.4f}."
    else:
        q1 = valid.quantile(0.25)
        q3 = valid.quantile(0.75)
        iqr = q3 - q1
        low = q1 - 1.5 * iqr
        high = q3 + 1.5 * iqr
        mask = (s < low) | (s > high)
        rule = f"IQR rule: Q1={q1:.4f}, Q3={q3:.4f}, IQR={iqr:.4f}; bounds={low:.4f} to {high:.4f}."
    out = df.loc[mask.fillna(False)].copy()
    out["_anomaly_reason"] = rule
    return out, rule


def make_chart(df, chart_type, x, y=None, color=None, title=None):
    chart_type = (chart_type or "").lower()
    if x not in df.columns:
        raise ValueError(f"Chart x column not found: {x}")
    if y and y not in df.columns:
        raise ValueError(f"Chart y column not found: {y}")
    color_col = color if color in df.columns else None
    if chart_type == "bar":
        fig = px.bar(df, x=x, y=y, color=color_col, title=title)
    elif chart_type == "line":
        fig = px.line(df, x=x, y=y, color=color_col, title=title, markers=True)
    elif chart_type == "pie":
        fig = px.pie(df, names=x, values=y, title=title)
    elif chart_type == "scatter":
        fig = px.scatter(df, x=x, y=y, color=color_col, title=title)
    elif chart_type == "histogram":
        fig = px.histogram(df, x=x, color=color_col, title=title)
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")
    fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
    return fig


def forecast_series(df, date_col, value_col, periods=6):
    if date_col not in df.columns or value_col not in df.columns:
        raise ValueError("Forecast columns were not found.")
    x = df[[date_col, value_col]].copy()
    x[date_col] = pd.to_datetime(x[date_col], errors="coerce")
    x[value_col] = pd.to_numeric(x[value_col], errors="coerce")
    x = x.dropna().sort_values(date_col)
    if len(x) < 3:
        raise ValueError("At least 3 valid observations are required for forecasting.")
    xi = np.arange(len(x), dtype=float)
    yi = x[value_col].to_numpy(dtype=float)
    slope, intercept = np.polyfit(xi, yi, 1)
    freq = pd.infer_freq(x[date_col]) or "D"
    future_dates = pd.date_range(start=x[date_col].iloc[-1], periods=periods + 1, freq=freq)[1:]
    future_x = np.arange(len(x), len(x) + periods, dtype=float)
    pred = slope * future_x + intercept
    return pd.DataFrame({date_col: future_dates, "forecast": pred})


def pandas_code_template(operation, columns):
    group = columns.get("group")
    metric = columns.get("metric")
    agg = columns.get("aggregation", "sum")
    n = columns.get("n", 5)
    filter_column = columns.get("filter_column")
    filter_value = columns.get("filter_value")
    if operation == "groupby":
        return f"result = df.groupby({group!r}, dropna=False)[{metric!r}].{agg}().sort_values(ascending=False).reset_index()"
    if operation == "top_n":
        return f"result = df.nlargest({int(n)}, {metric!r})"
    if operation == "filter":
        return f"result = df[df[{filter_column!r}].astype(str).str.casefold() == {str(filter_value).casefold()!r}]"
    if operation == "summary":
        return "result = df.describe(include='all', datetime_is_numeric=True).transpose()"
    if operation == "anomaly":
        return f"# Apply IQR/z-score outlier detection to df[{metric!r}]"
    return "# Pandas code is not required for this operation."
