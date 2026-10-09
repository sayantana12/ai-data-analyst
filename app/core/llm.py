import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()

GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


SYSTEM_PROMPT = """
You are the AI Analyst Agent inside a production-oriented CSV analytics application.

Your job is to reason about the user's question, choose and call the appropriate
local analytics tools, inspect their results, call additional tools when needed,
and then give an evidence-grounded answer.

IMPORTANT RULES:

1. DATA SOURCE
- The uploaded dataset is the source of truth.
- Never invent values, columns, rows, dates, metrics, or findings.
- Never assume a column exists without checking the supplied dataset schema.
- If the requested information is not available in the dataset, say so clearly.

2. TOOL USAGE
- You do NOT directly execute Python or SQL.
- You call the available tools and the application executes them.
- Prefer analytical tools for factual claims about uploaded data.
- You may make multiple sequential tool calls when a question requires multiple steps.
- Before the final answer, check whether the tool results actually support the conclusion.

3. NATURAL-LANGUAGE ANALYSIS
- Understand the user's analytical intent from the natural-language question.
- Map the intent to the appropriate dataset columns using the schema and examples.
- Do not rely on fixed column names.
- Do not invent a metric, category, date column, or filter value.

4. CHARTS AND VISUALIZATIONS
- Whenever the user asks to show, create, generate, plot, visualize, graph,
  chart, trend, distribution, comparison, relationship, or similar visual output,
  you MUST call the create_chart tool.
- Do not answer a visualization request with text or a table alone.
- Choose the chart type based on the analytical intent:
    * line -> time-based trends
    * bar -> category comparisons/rankings
    * pie -> part-to-whole comparisons
    * scatter -> relationship between two numeric variables
    * histogram -> distribution of a numeric variable
- Select x, y, color, aggregation, and date_granularity from the actual dataset schema.
- Never invent column names.
- For time-based analysis, use date_granularity when appropriate.
- For aggregated charts, use an appropriate aggregation such as sum, mean, min,
  max, or count.
- After create_chart returns, use its returned data as evidence for the answer.
- Never claim that a chart was created unless create_chart was actually called
  successfully and returned usable chart data.

5. BUSINESS INSIGHTS
- Answer business questions using actual computed results.
- Explain important patterns and comparisons supported by the returned data.
- Do not fabricate business conclusions.

6. ANOMALY DETECTION
- Use detect_anomalies for anomaly requests.
- Explain the statistical rule returned by the tool.
- Do not call a value anomalous unless the tool flagged it.

7. FORECASTING
- Use the forecast tool for forecasting requests.
- Clearly identify the result as a forecast.
- State the forecasting method returned by the tool.
- Do not present predictions as historical facts.

8. SQL
- When the user explicitly asks for SQL, generate safe read-only SQL.
- Use SELECT or WITH queries only.
- When the user asks for an analysis rather than SQL specifically,
  use the analytical tools to actually compute the result.

9. PANDAS
- When the user explicitly asks for Pandas code, generate safe inspection-only
  Pandas code through generate_pandas_code.
- The generated code is for display and inspection.
- Do not execute arbitrary model-generated Python.

10. CODE GENERATION WHEN APPROPRIATE
- For analytical requests where SQL and/or Pandas code is useful,
  the application may request generated code in addition to computing the result.
- Never replace the actual dataset computation with fabricated code output.

11. MULTI-STEP ANALYSIS
- You may call multiple tools.
- For example:
    schema -> SQL/Pandas analysis -> chart -> final explanation.
- Use additional tools whenever they are necessary to answer the question correctly.

12. CONVERSATION CONTEXT
- Use recent conversation context when interpreting follow-up questions.
- A follow-up such as "show that as a chart" refers to the previous analytical
  result when the relevant context exists.
- Do not lose the meaning of the previous question.

13. FINAL RESPONSE
- The final answer must be concise but useful.
- Use only evidence returned by tools.
- Include a short "Reasoning summary" section describing the analytical operations
  performed and the evidence used.
- Do not expose private chain-of-thought.
- Never claim that an operation succeeded if the corresponding tool failed.

AVAILABLE TOOLS:

inspect_schema
execute_sql
generate_sql
run_pandas_analysis
create_chart
detect_anomalies
forecast
semantic_search
data_quality_check
create_dashboard
generate_pandas_code
"""


def schema_context(df):
    rows = []

    for col in df.columns:
        s = df[col]

        rows.append(
            {
                "name": str(col),
                "dtype": str(s.dtype),
                "missing": int(s.isna().sum()),
                "unique": int(s.nunique(dropna=True)),
                "examples": s.dropna().astype(str).head(3).tolist(),
            }
        )

    return {
        "rows": int(len(df)),
        "columns": rows,
    }


def function_declarations():
    """
    Gemini function-calling declarations.

    Gemini decides which tool to call.
    The Python application executes the selected tool.
    """

    return [
        {
            "name": "inspect_schema",
            "description": (
                "Inspect the uploaded dataset schema, data types, missing counts, "
                "unique counts, and examples."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
        {
            "name": "execute_sql",
            "description": (
                "Execute a read-only SELECT/WITH SQL query against the in-memory "
                "table named data. Use for aggregations, rankings, filtering, "
                "grouping, and other supported analytical queries."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": (
                            "A read-only SELECT or WITH query using table data."
                        ),
                    }
                },
                "required": ["sql"],
            },
        },
        {
            "name": "generate_sql",
            "description": (
                "Generate safe read-only SQL for the requested analysis without "
                "executing it. Use when the user explicitly asks to see SQL."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": (
                            "Read-only SELECT/WITH SQL using table data."
                        ),
                    }
                },
                "required": ["sql"],
            },
        },
        {
            "name": "run_pandas_analysis",
            "description": (
                "Run a safe predefined Pandas analysis operation without executing "
                "arbitrary model-generated Python."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "summary",
                            "groupby",
                            "top_n",
                            "filter",
                        ],
                    },
                    "group": {
                        "type": "string",
                    },
                    "metric": {
                        "type": "string",
                    },
                    "aggregation": {
                        "type": "string",
                        "enum": [
                            "sum",
                            "mean",
                            "min",
                            "max",
                            "count",
                        ],
                    },
                    "n": {
                        "type": "integer",
                    },
                    "filter_column": {
                        "type": "string",
                    },
                    "filter_value": {
                        "type": "string",
                    },
                },
                "required": ["operation"],
            },
        },
        {
            "name": "create_chart",
            "description": (
                "Create the visualization requested by the user from the uploaded "
                "dataset. MUST be called whenever the user asks for a chart, graph, "
                "plot, visualization, trend, distribution, comparison, or relationship. "
                "Supports bar, line, pie, scatter, and histogram. Select x/y/color and "
                "aggregation using only actual dataset columns. Returns chart metadata "
                "and serializable chart data for the UI."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "chart_type": {
                        "type": "string",
                        "enum": [
                            "bar",
                            "line",
                            "pie",
                            "scatter",
                            "histogram",
                        ],
                    },
                    "x": {
                        "type": "string",
                    },
                    "y": {
                        "type": "string",
                    },
                    "color": {
                        "type": "string",
                    },
                    "aggregation": {
                        "type": "string",
                        "enum": [
                            "sum",
                            "mean",
                            "min",
                            "max",
                            "count",
                        ],
                    },
                    "title": {
                        "type": "string",
                    },
                    "date_granularity": {
                        "type": "string",
                        "enum": [
                            "day",
                            "month",
                            "quarter",
                            "year",
                        ],
                    },
                },
                "required": [
                    "chart_type",
                    "x",
                ],
            },
        },
        {
            "name": "detect_anomalies",
            "description": (
                "Detect statistical outliers in a numeric column using IQR or "
                "z-score and return flagged rows plus the exact rule."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "column": {
                        "type": "string",
                    },
                    "method": {
                        "type": "string",
                        "enum": [
                            "iqr",
                            "zscore",
                        ],
                    },
                    "threshold": {
                        "type": "number",
                    },
                },
                "required": [
                    "column",
                ],
            },
        },
        {
            "name": "forecast",
            "description": (
                "Create a lightweight CPU forecast for a date/time series using "
                "a transparent linear trend model."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "date_column": {
                        "type": "string",
                    },
                    "value_column": {
                        "type": "string",
                    },
                    "periods": {
                        "type": "integer",
                    },
                },
                "required": [
                    "date_column",
                    "value_column",
                    "periods",
                ],
            },
        },
        {
            "name": "semantic_search",
            "description": (
                "Find rows most semantically related to a natural-language query "
                "using a local TF-IDF search over row text."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                    },
                    "top_k": {
                        "type": "integer",
                    },
                },
                "required": [
                    "query",
                ],
            },
        },
        {
            "name": "data_quality_check",
            "description": (
                "Run data quality checks including missing values, duplicates, "
                "data types, and basic column statistics."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
        {
            "name": "create_dashboard",
            "description": (
                "Generate a dashboard specification and computed datasets for "
                "KPIs and charts based on the uploaded data."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "metric": {
                        "type": "string",
                    },
                    "category": {
                        "type": "string",
                    },
                    "date_column": {
                        "type": "string",
                    },
                    "title": {
                        "type": "string",
                    },
                },
                "required": [],
            },
        },
        {
            "name": "generate_pandas_code",
            "description": (
                "Generate safe, non-executed Pandas code for an analysis request. "
                "The code is displayed for inspection only."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "groupby",
                            "top_n",
                            "filter",
                            "summary",
                            "anomaly",
                        ],
                    },
                    "group": {
                        "type": "string",
                    },
                    "metric": {
                        "type": "string",
                    },
                    "aggregation": {
                        "type": "string",
                        "enum": [
                            "sum",
                            "mean",
                            "min",
                            "max",
                            "count",
                        ],
                    },
                    "n": {
                        "type": "integer",
                    },
                    "filter_column": {
                        "type": "string",
                    },
                    "filter_value": {
                        "type": "string",
                    },
                },
                "required": [
                    "operation",
                ],
            },
        },
    ]


def _post(contents, tools=None, temperature=0.1):
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    payload = {
        "system_instruction": {
            "parts": [
                {
                    "text": SYSTEM_PROMPT,
                }
            ]
        },
        "contents": contents,
        "tools": [
            {
                "function_declarations": function_declarations(),
            }
        ],
        "generationConfig": {
            "temperature": temperature,
        },
    }

    url = (
        f"{GEMINI_BASE}/"
        f"{GEMINI_MODEL}:generateContent"
        f"?key={GEMINI_API_KEY}"
    )

    response = requests.post(
        url,
        json=payload,
        timeout=60,
    )

    if not response.ok:
        raise RuntimeError(
            f"Gemini API error {response.status_code}: "
            f"{response.text[:700]}"
        )

    return response.json()


def initial_contents(question, df, history):
    context = {
        "dataset": schema_context(df),
        "recent_conversation": [
            {
                "role": m.get("role"),
                "content": str(
                    m.get("content", "")
                )[:1200],
            }
            for m in history[-8:]
        ],
        "current_question": question,
    }

    return [
        {
            "role": "user",
            "parts": [
                {
                    "text": json.dumps(
                        context,
                        default=str,
                    )
                }
            ],
        }
    ]


def parse_function_calls(response):
    calls = []

    candidates = response.get(
        "candidates",
        [],
    )

    if not candidates:
        return calls, None

    content = candidates[0].get(
        "content",
        {},
    )

    for part in content.get(
        "parts",
        [],
    ):
        function_call = part.get(
            "functionCall"
        )

        if function_call:
            calls.append(function_call)

    return calls, content


def final_text(response):
    candidates = response.get(
        "candidates",
        [],
    )

    if not candidates:
        return ""

    parts = candidates[0].get(
        "content",
        {},
    ).get(
        "parts",
        [],
    )

    return "\n".join(
        part.get("text", "")
        for part in parts
        if part.get("text")
    )


def make_function_response(
    name,
    result,
    call_id=None,
):
    function_response = {
        "name": name,
        "response": result,
    }

    if call_id:
        function_response["id"] = call_id

    return {
        "functionResponse": function_response
    }


def stream_final_explanation(
    question,
    tool_trace,
):
    """
    Stream only the final evidence-grounded explanation
    after tool execution.
    """

    if not GEMINI_API_KEY:
        yield "Streaming requires GEMINI_API_KEY."
        return

    evidence = json.dumps(
        tool_trace,
        default=str,
    )

    prompt = f"""
Question:
{question}

Tool evidence from the local analytics agent:
{evidence[:30000]}

Write the final answer using only this evidence.

Include a short section called:
Reasoning summary

The reasoning summary should describe concise,
auditable analytical steps and should NOT expose
private chain-of-thought.

Do not invent values, columns, or findings.

If a chart was generated, acknowledge the chart
using only the returned chart evidence.
"""

    payload = {
        "system_instruction": {
            "parts": [
                {
                    "text": SYSTEM_PROMPT,
                }
            ]
        },
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": prompt,
                    }
                ],
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
        },
    }

    url = (
        f"{GEMINI_BASE}/"
        f"{GEMINI_MODEL}:streamGenerateContent"
        f"?alt=sse&key={GEMINI_API_KEY}"
    )

    with requests.post(
        url,
        json=payload,
        stream=True,
        timeout=60,
    ) as response:

        if not response.ok:
            yield (
                f"Streaming error: "
                f"{response.status_code}"
            )
            return

        for raw in response.iter_lines(
            decode_unicode=True
        ):
            if not raw:
                continue

            if not raw.startswith("data:"):
                continue

            try:
                obj = json.loads(
                    raw[5:].strip()
                )

                parts = (
                    obj.get(
                        "candidates",
                        [{}],
                    )[0]
                    .get(
                        "content",
                        {},
                    )
                    .get(
                        "parts",
                        [],
                    )
                )

                for part in parts:
                    if part.get("text"):
                        yield part["text"]

            except Exception:
                continue