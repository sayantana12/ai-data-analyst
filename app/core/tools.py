import json
import pandas as pd
from app.core.analytics import (
    execute_sql, detect_anomalies, make_chart, forecast_series,
    pandas_code_template, safe_identifier,
)
from app.core.data_manager import dataset_profile, data_quality_report
from app.core.search import semantic_search


def _records(df, n=100):
    return json.loads(df.head(n).to_json(orient="records", date_format="iso"))


def tool_inspect_schema(df, **_):
    return {"schema": json.loads(dataset_profile(df).to_json(orient="records")), "rows": len(df), "columns": len(df.columns)}


def tool_generate_sql(df, sql, **_):
    # Validate syntax policy without executing the query.
    cleaned = sql.strip().rstrip(";")
    if not cleaned.lower().startswith(("select", "with")):
        raise ValueError("Generated SQL must be read-only SELECT/WITH.")
    return {"sql": cleaned, "executed": False}


def tool_execute_sql(df, sql, **_):
    result = execute_sql(df, sql)
    return {"columns": list(result.columns), "rows": _records(result), "row_count": len(result), "sql": sql}


def tool_run_pandas_analysis(df, operation, group=None, metric=None, aggregation="sum", n=5, filter_column=None, filter_value=None, **_):
    if operation == "summary":
        out = df.describe(include="all", datetime_is_numeric=True).transpose().reset_index().rename(columns={"index": "column"})
    elif operation == "groupby":
        if group not in df.columns or metric not in df.columns:
            raise ValueError("group and metric must be existing columns")
        if aggregation not in {"sum", "mean", "min", "max", "count"}:
            raise ValueError("Unsupported aggregation")
        out = df.groupby(group, dropna=False)[metric].agg(aggregation).sort_values(ascending=False).reset_index()
    elif operation == "top_n":
        if metric not in df.columns:
            raise ValueError("metric must be an existing column")
        out = df.nlargest(int(n), metric)
    elif operation == "filter":
        if filter_column not in df.columns:
            raise ValueError("filter_column must be an existing column")
        out = df[df[filter_column].astype(str).str.casefold() == str(filter_value).casefold()]
    else:
        raise ValueError("Unknown Pandas analysis operation")
    return {"rows": _records(out), "row_count": len(out), "columns": list(out.columns)}


def tool_create_chart(df, chart_type, x, y=None, color=None, aggregation=None, title=None, date_granularity=None, **_):
    work = df.copy()
    if date_granularity and x in work.columns:
        dt = pd.to_datetime(work[x], errors="coerce")
        if date_granularity == "month":
            work["__period"] = dt.dt.to_period("M").astype(str)
        elif date_granularity == "quarter":
            work["__period"] = dt.dt.to_period("Q").astype(str)
        elif date_granularity == "year":
            work["__period"] = dt.dt.year.astype("Int64").astype(str)
        else:
            work["__period"] = dt.dt.date.astype(str)
        x = "__period"

    if aggregation and y and x in work.columns and y in work.columns:
        agg = aggregation if aggregation in {"sum", "mean", "min", "max", "count"} else "sum"
        work = work.groupby(x, dropna=False)[y].agg(agg).reset_index()

    fig = make_chart(work, chart_type, x, y, color, title)
    # Store a serializable representation for report/UI; the UI recreates Plotly figure from data.
    selected = [c for c in [x, y, color] if c and c in work.columns]
    return {
        "chart_type": chart_type,
        "title": title or "Generated chart",
        "x": x,
        "y": y,
        "color": color,
        "data": _records(work[selected]),
        "columns": selected,
    }


def tool_detect_anomalies(df, column, method="iqr", threshold=None, **_):
    out, rule = detect_anomalies(df, column, method=method)
    return {"column": column, "method": method, "rule": rule, "rows": _records(out), "count": len(out)}


def tool_forecast(df, date_column, value_column, periods=6, **_):
    out = forecast_series(df, date_column, value_column, int(periods))
    return {"date_column": date_column, "value_column": value_column, "periods": int(periods), "method": "linear trend regression over time index", "rows": _records(out)}


def tool_semantic_search(df, query, top_k=10, **_):
    out = semantic_search(df, query, int(top_k))
    return {"query": query, "rows": _records(out), "count": len(out)}


def tool_data_quality(df, **_):
    q = data_quality_report(df)
    return {
        "rows": q["rows"], "columns": q["columns"], "missing_cells": q["missing_cells"],
        "duplicate_rows": q["duplicate_rows"], "column_report": json.loads(q["columns"].to_json(orient="records")),
    }


def tool_dashboard(df, metric=None, category=None, date_column=None, title=None, **_):
    numeric = df.select_dtypes(include="number").columns.tolist()
    categorical = df.select_dtypes(exclude="number").columns.tolist()
    metric = metric if metric in df.columns else (numeric[0] if numeric else None)
    category = category if category in df.columns else (categorical[0] if categorical else None)
    date_column = date_column if date_column in df.columns else None

    kpis = {}
    if metric:
        s = pd.to_numeric(df[metric], errors="coerce")
        kpis = {"metric": metric, "total": float(s.sum()), "average": float(s.mean()), "min": float(s.min()), "max": float(s.max())}

    widgets = []
    if category and metric:
        grouped = df.groupby(category, dropna=False)[metric].sum().sort_values(ascending=False).head(15).reset_index()
        widgets.append({"type": "bar", "title": f"{metric} by {category}", "data": _records(grouped), "x": category, "y": metric})
    if date_column and metric:
        dt = pd.to_datetime(df[date_column], errors="coerce")
        temp = pd.DataFrame({"date": dt, "value": pd.to_numeric(df[metric], errors="coerce")}).dropna()
        monthly = temp.groupby(temp["date"].dt.to_period("M")).sum(numeric_only=True).reset_index()
        monthly["date"] = monthly["date"].astype(str)
        widgets.append({"type": "line", "title": f"Monthly {metric} trend", "data": _records(monthly), "x": "date", "y": "value"})
    return {"title": title or "AI Generated Dashboard", "kpis": kpis, "widgets": widgets}


def tool_pandas_code(operation, group=None, metric=None, aggregation="sum", n=5, filter_column=None, filter_value=None, **_):
    return {"code": pandas_code_template(operation, {"group": group, "metric": metric, "aggregation": aggregation, "n": n, "filter_column": filter_column, "filter_value": filter_value})}


TOOL_MAP = {
    "inspect_schema": tool_inspect_schema,
    "generate_sql": tool_generate_sql,
    "execute_sql": tool_execute_sql,
    "run_pandas_analysis": tool_run_pandas_analysis,
    "create_chart": tool_create_chart,
    "detect_anomalies": tool_detect_anomalies,
    "forecast": tool_forecast,
    "semantic_search": tool_semantic_search,
    "data_quality_check": tool_data_quality,
    "create_dashboard": tool_dashboard,
    "generate_pandas_code": tool_pandas_code,
}
