import json
import logging

import pandas as pd
import requests

from app.core.llm import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GEMINI_BASE,
    initial_contents,
    function_declarations,
    parse_function_calls,
    final_text,
    make_function_response,
    SYSTEM_PROMPT,
    stream_final_explanation,
)

from app.core.tools import TOOL_MAP
from app.core.analytics import make_chart


logger = logging.getLogger(
    "ai_data_analyst.agent"
)


def _fallback(df, question):
    """
    Deterministic fallback used when Gemini is unavailable.

    This does not invent analytical values.
    It selects an existing local tool using the
    uploaded dataframe structure.
    """

    q = question.lower()

    numeric = (
        df.select_dtypes(
            include="number"
        )
        .columns
        .tolist()
    )

    categorical = (
        df.select_dtypes(
            exclude="number"
        )
        .columns
        .tolist()
    )

    date_cols = [
        column
        for column in df.columns
        if (
            "date" in str(column).lower()
            or "time" in str(column).lower()
        )
    ]

    # Anomaly detection
    if "anomal" in q and numeric:
        return [
            "detect_anomalies",
            {
                "column": numeric[0],
                "method": "iqr",
            },
        ]

    # Forecasting
    if (
        "forecast" in q
        and numeric
        and date_cols
    ):
        return [
            "forecast",
            {
                "date_column": date_cols[0],
                "value_column": numeric[0],
                "periods": 6,
            },
        ]

    # Data quality
    if (
        "quality" in q
        or "missing" in q
        or "duplicate" in q
    ):
        return [
            "data_quality_check",
            {},
        ]

    # Explicit SQL request
    if "sql" in q:
        return [
            "generate_sql",
            {
                "sql": "SELECT * FROM data LIMIT 10",
            },
        ]

    # Chart / trend fallback
    if (
        (
            "chart" in q
            or "graph" in q
            or "plot" in q
            or "visual" in q
            or "trend" in q
            or "monthly" in q
        )
        and numeric
        and date_cols
    ):
        return [
            "create_chart",
            {
                "chart_type": "line",
                "x": date_cols[0],
                "y": numeric[0],
                "date_granularity": "month",
                "aggregation": "sum",
                "title": question,
            },
        ]

    # Top-N fallback
    if "top" in q and numeric:
        return [
            "run_pandas_analysis",
            {
                "operation": "top_n",
                "metric": numeric[0],
                "n": 5,
            },
        ]

    # Basic category/metric analysis
    if numeric and categorical:
        return [
            "run_pandas_analysis",
            {
                "operation": "groupby",
                "group": categorical[0],
                "metric": numeric[0],
                "aggregation": "sum",
            },
        ]

    return [
        "inspect_schema",
        {},
    ]


def _gemini_turn(contents):
    """
    Send one Gemini tool-calling turn.
    """

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured"
        )

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
                "function_declarations":
                    function_declarations()
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
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
            f"Gemini API error "
            f"{response.status_code}: "
            f"{response.text[:700]}"
        )

    return response.json()


def _clean_tool_result(result):
    """
    Keep tool results bounded before they are sent
    back into the LLM context.
    """

    raw = json.dumps(
        result,
        default=str,
    )

    if len(raw) > 14000:

        if (
            isinstance(result, dict)
            and "rows" in result
            and isinstance(
                result["rows"],
                list,
            )
        ):
            result = dict(result)

            result["rows"] = (
                result["rows"][:50]
            )

            result[
                "truncated_for_model_context"
            ] = True

        raw = json.dumps(
            result,
            default=str,
        )

    return result, raw


def _capture_tool_artifact(
    name,
    args,
    result,
    state,
):
    """
    Capture tables, charts, anomalies,
    forecasts, generated code, SQL and dashboards
    for the Streamlit UI.
    """

    if name == "execute_sql":

        state["sql"] = args.get(
            "sql"
        )

        if "rows" in result:
            state["table"] = pd.DataFrame(
                result["rows"]
            )

    elif name == "generate_sql":

        state["sql"] = result.get(
            "sql"
        )

    elif name == "run_pandas_analysis":

        if "rows" in result:
            state["table"] = pd.DataFrame(
                result["rows"]
            )

    elif name == "create_chart":

        state["chart_meta"] = result

        data = result.get(
            "data",
            [],
        )

        if data:

            chart_df = pd.DataFrame(
                data
            )

            try:
                state["chart"] = make_chart(
                    chart_df,
                    result.get(
                        "chart_type"
                    ),
                    result.get("x"),
                    result.get("y"),
                    result.get("color"),
                    result.get("title"),
                )

            except Exception as exc:

                logger.exception(
                    "Failed to rebuild chart: %s",
                    exc,
                )

                state["chart"] = None

        else:
            state["chart"] = None

    elif name == "detect_anomalies":

        state["anomalies"] = pd.DataFrame(
            result.get(
                "rows",
                [],
            )
        )

    elif name == "forecast":

        state["forecast"] = pd.DataFrame(
            result.get(
                "rows",
                [],
            )
        )

    elif name == "generate_pandas_code":

        state["code"] = result.get(
            "code"
        )

    elif name == "create_dashboard":

        state["dashboard"] = result


def run_agent(
    df,
    question,
    history,
    stream_final=False,
):
    """
    Main AI analyst entry point.

    Flow:

        User question
             ↓
        Gemini
             ↓
        Tool call
             ↓
        Local Pandas / SQL / chart execution
             ↓
        Tool result
             ↓
        Gemini
             ↓
        Evidence-grounded answer
    """

    contents = initial_contents(
        question,
        df,
        history,
    )

    tool_trace = []

    max_steps = 8

    final = ""

    state = {
        "chart": None,
        "chart_meta": None,
        "anomalies": None,
        "forecast": None,
        "table": None,
        "sql": None,
        "code": None,
        "dashboard": None,
    }

    try:

        for step in range(max_steps):

            response = _gemini_turn(
                contents
            )

            calls, model_content = (
                parse_function_calls(
                    response
                )
            )

            # Preserve Gemini's model turn,
            # including function calls.
            if model_content:
                contents.append(
                    model_content
                )

            # No tool call means Gemini has
            # produced the final answer.
            if not calls:

                final = final_text(
                    response
                )

                break

            function_parts = []

            for call in calls:

                name = call.get(
                    "name"
                )

                args = call.get(
                    "args"
                ) or {}

                if name not in TOOL_MAP:

                    result = {
                        "error": (
                            f"Unknown tool: "
                            f"{name}"
                        )
                    }

                else:

                    try:

                        result = TOOL_MAP[
                            name
                        ](
                            df,
                            **args
                        )

                    except Exception as exc:

                        logger.exception(
                            "Tool failed: %s",
                            name,
                        )

                        result = {
                            "error": str(
                                exc
                            ),
                            "tool": name,
                        }

                result, raw = (
                    _clean_tool_result(
                        result
                    )
                )

                tool_trace.append(
                    {
                        "step": step + 1,
                        "tool": name,
                        "arguments": args,
                        "result": result,
                    }
                )

                logger.info(
                    "tool_call step=%s tool=%s args=%s",
                    step + 1,
                    name,
                    args,
                )

                # Capture all UI artifacts.
                _capture_tool_artifact(
                    name,
                    args,
                    result,
                    state,
                )

                function_parts.append(
                    make_function_response(
                        name,
                        result,
                        call.get("id"),
                    )
                )

            # Send tool outputs back to Gemini.
            contents.append(
                {
                    "role": "user",
                    "parts": function_parts,
                }
            )

        else:

            final = (
                "The analysis reached the "
                "maximum tool-call steps. "
                "Please narrow the question."
            )

    except Exception as exc:

        logger.exception(
            "Gemini analysis failed: %s",
            exc,
        )

        # Deterministic local fallback.
        if (
            not GEMINI_API_KEY
            or "Gemini API error"
            in str(exc)
            or "not configured"
            in str(exc)
        ):

            name, args = _fallback(
                df,
                question,
            )

            try:

                result = TOOL_MAP[
                    name
                ](
                    df,
                    **args
                )

            except Exception as fallback_exc:

                logger.exception(
                    "Fallback analysis failed: %s",
                    fallback_exc,
                )

                result = {
                    "error": str(
                        fallback_exc
                    )
                }

            tool_trace.append(
                {
                    "step": 1,
                    "tool": name,
                    "arguments": args,
                    "result": result,
                    "fallback": True,
                }
            )

            _capture_tool_artifact(
                name,
                args,
                result,
                state,
            )

            final = (
                "Gemini was unavailable, so "
                "a deterministic local analysis "
                "was used. The result below is "
                "computed from the uploaded data."
            )

        else:
            raise

    # Optional streaming final explanation.
    if (
        stream_final
        and GEMINI_API_KEY
        and tool_trace
    ):

        streamed = "".join(
            stream_final_explanation(
                question,
                tool_trace,
            )
        )

        if streamed.strip():
            final = streamed

    if not final:

        final = (
            "The tools returned results, "
            "but the LLM did not provide "
            "a final response."
        )

    # Concise auditable reasoning summary.
    reasoning_lines = []

    for i, trace in enumerate(
        tool_trace,
        1,
    ):

        reasoning_lines.append(
            f"{i}. Used `{trace['tool']}` "
            "with the requested dataset "
            "operation and inspected its "
            "returned evidence."
        )

    if not reasoning_lines:

        reasoning_lines.append(
            "The LLM did not call an "
            "analytical tool for this response."
        )

    reasoning = "\n".join(
        reasoning_lines
    )

    return {
        "question": question,
        "answer": final,
        "reasoning": reasoning,
        "plan": {
            "agentic": True,
            "max_steps": max_steps,
            "tool_calls": len(
                tool_trace
            ),
        },
        "tool_trace": tool_trace,
        "table": state["table"],
        "chart": state["chart"],
        "chart_meta": state[
            "chart_meta"
        ],
        "anomalies": state[
            "anomalies"
        ],
        "forecast": state[
            "forecast"
        ],
        "dashboard": state[
            "dashboard"
        ],
        "sql": state["sql"],
        "code": state["code"],
    }