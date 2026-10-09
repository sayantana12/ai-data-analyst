
import html
import json


def _table_html(df):
    if df is None:
        return ""
    try:
        return df.head(100).to_html(index=False, escape=True)
    except Exception:
        return ""


def build_html_report(question, answer, reasoning, sql, code, plan, table=None, anomalies=None, forecast=None):
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>AI Data Analyst Report</title>
<style>
body {{ font-family: Arial, sans-serif; max-width: 1100px; margin: 40px auto; padding: 0 20px; }}
pre {{ background: #f4f4f4; padding: 14px; overflow-x: auto; }}
table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
th, td {{ border: 1px solid #ddd; padding: 7px; text-align: left; }}
h1, h2 {{ margin-top: 28px; }}
</style>
</head>
<body>
<h1>AI Data Analyst Report</h1>
<h2>Question</h2>
<p>{html.escape(str(question))}</p>
<h2>Answer</h2>
<p>{html.escape(str(answer))}</p>
<h2>Reasoning / explanation</h2>
<p>{html.escape(str(reasoning))}</p>
<h2>Execution plan</h2>
<pre>{html.escape(json.dumps(plan, indent=2, default=str))}</pre>
{"<h2>Generated SQL</h2><pre>" + html.escape(str(sql)) + "</pre>" if sql else ""}
{"<h2>Generated Pandas code</h2><pre>" + html.escape(str(code)) + "</pre>" if code else ""}
{"<h2>Result</h2>" + _table_html(table) if table is not None else ""}
{"<h2>Anomalies</h2>" + _table_html(anomalies) if anomalies is not None else ""}
{"<h2>Forecast</h2>" + _table_html(forecast) if forecast is not None else ""}
</body>
</html>"""
