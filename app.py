import os
import json
import logging
from datetime import datetime

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from app.core.data_manager import validate_csv, combine_files, dataset_profile, data_quality_report
from app.core.agent import run_agent
from app.core.report import build_html_report

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

st.set_page_config(page_title="AI Data Analyst", page_icon="📊", layout="wide")

AUTH_PASSWORD = os.getenv("APP_PASSWORD", "").strip()
if AUTH_PASSWORD:
    if not st.session_state.get("authenticated", False):
        st.title("🔐 AI Data Analyst")
        password = st.text_input("Password", type="password")
        if st.button("Sign in", type="primary"):
            if password == AUTH_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            st.error("Invalid password.")
        st.stop()

for key, default in {
    "messages": [], "df": None, "file_names": [], "last_result": None, "upload_signature": None
}.items():
    st.session_state.setdefault(key, default)

with st.sidebar:
    st.header("📁 Data sources")
    uploaded = st.file_uploader(
        "Upload one or more CSV files",
        type=["csv"],
        accept_multiple_files=True,
        help="Each file is validated before being added to the session dataset.",
    )

    if uploaded:
        # Streamlit reruns this script after every chat submission while the
        # file_uploader still contains the same UploadedFile objects. Do NOT
        # clear conversation history on those normal reruns.
        upload_signature = tuple(
            (f.name, getattr(f, "size", None), getattr(f, "file_id", None))
            for f in uploaded
        )

        if upload_signature != st.session_state.get("upload_signature"):
            frames, names, errors = [], [], []
            for f in uploaded:
                ok, message, frame = validate_csv(f)
                if ok:
                    frames.append(frame)
                    names.append(f.name)
                else:
                    errors.append(f"{f.name}: {message}")

            for error in errors:
                st.error(error)

            if frames:
                try:
                    st.session_state.df = combine_files(frames, names)
                    st.session_state.file_names = names

                    # A genuinely new CSV selection starts a new analytical
                    # session. The same selection keeps its conversation.
                    st.session_state.messages = []
                    st.session_state.last_result = None
                    st.session_state.upload_signature = upload_signature

                    st.success(f"Loaded {len(frames)} CSV file(s).")
                except Exception as exc:
                    st.error(f"Could not load files: {exc}")

    if st.session_state.df is not None:
        df = st.session_state.df
        st.metric("Rows", f"{len(df):,}")
        st.metric("Columns", f"{len(df.columns):,}")
        st.caption("Sources: " + ", ".join(st.session_state.file_names))
        q = data_quality_report(df)
        st.write(f"Missing cells: **{q['missing_cells']:,}**")
        st.write(f"Duplicate rows: **{q['duplicate_rows']:,}**")
        if st.button("Clear session", use_container_width=True):
            st.session_state.df = None
            st.session_state.file_names = []
            st.session_state.messages = []
            st.session_state.last_result = None
            st.session_state.upload_signature = None
            st.rerun()

    st.divider()
    stream_final = st.checkbox("Stream final LLM explanation", value=False, help="Streams the final evidence-grounded explanation after the agent finishes its tool calls.")
    st.caption("LLM = reasoning/orchestration. Analytics = local CPU tools. No GPU required.")

st.title("📊 AI-Powered Data Analyst")
st.caption("An LLM-driven analytical agent for CSV data — not a simple LLM question-answer wrapper.")

if st.session_state.df is None:
    st.info("Upload one or more CSV files from the sidebar to begin.")
    st.markdown("""
**Example questions**
- Which region generated the highest revenue?
- Show monthly sales trends.
- Which products are underperforming?
- What are the top five customers?
- Generate SQL for this analysis.
- Detect anomalies in the dataset.
""")
    st.stop()

df = st.session_state.df

tab_chat, tab_data, tab_quality, tab_dashboard, tab_export = st.tabs(
    ["💬 AI Analyst", "🔎 Data", "🧪 Quality", "📈 Dashboard", "📄 Export"]
)

with tab_data:
    st.subheader("Dataset preview")
    st.dataframe(df.head(100), use_container_width=True)
    st.subheader("Schema and profiling")
    st.dataframe(dataset_profile(df), use_container_width=True)

with tab_quality:
    st.subheader("Data quality")
    q = data_quality_report(df)
    a, b, c, d = st.columns(4)
    a.metric("Rows", f"{q['rows']:,}")
    b.metric("Columns", len(q["columns"]))
    c.metric("Missing cells", f"{q['missing_cells']:,}")
    d.metric("Duplicate rows", f"{q['duplicate_rows']:,}")
    st.dataframe(q["columns"], use_container_width=True)

with tab_dashboard:
    st.subheader("AI dashboard generation")
    st.caption("Ask the agent to generate a dashboard, or use the last dashboard generated by the agent.")
    last = st.session_state.last_result
    dashboard = last.get("dashboard") if last else None
    if dashboard:
        kpis = dashboard.get("kpis", {})
        cols = st.columns(max(1, min(4, len(kpis))))
        for i, (key, value) in enumerate(kpis.items()):
            if key == "metric":
                continue
            cols[i % len(cols)].metric(key.replace("_", " ").title(), f"{value:,.2f}" if isinstance(value, (int, float)) else str(value))
        for widget in dashboard.get("widgets", []):
            st.markdown(f"**{widget.get('title', 'Chart')}**")
            chart_data = pd.DataFrame(widget.get("data", []))
            if widget.get("type") == "bar" and not chart_data.empty:
                st.bar_chart(chart_data.set_index(widget["x"])[widget["y"]])
            elif widget.get("type") == "line" and not chart_data.empty:
                st.line_chart(chart_data.set_index(widget["x"])[widget["y"]])
    else:
        st.info("Ask: `Create a sales dashboard` to let the LLM call the dashboard tool.")

with tab_chat:
    st.subheader("Ask the AI analyst")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sql"):
                with st.expander("Generated SQL"):
                    st.code(msg["sql"], language="sql")
            if msg.get("code"):
                with st.expander("Generated Pandas code"):
                    st.code(msg["code"], language="python")
            if msg.get("table") is not None:
                st.dataframe(msg["table"], use_container_width=True)
            if msg.get("chart") is not None:
                st.plotly_chart(msg["chart"], use_container_width=True)
            if msg.get("anomalies") is not None:
                meta = msg.get("anomaly_meta") or {}
                count = int(meta.get("count", len(msg["anomalies"])))
                with st.expander("Anomaly detection", expanded=True):
                    if count:
                        st.warning(f"🚨 {count} anomal{"y" if count == 1 else "ies"} detected in `{meta.get("column", "numeric data")}`.")
                        st.dataframe(msg["anomalies"], use_container_width=True)
                    else:
                        st.success(f"✅ No anomalies detected in `{meta.get("column", "the numeric data")}` using the {str(meta.get("method", "IQR")).upper()} method.")
                    if meta.get("rule"):
                        st.caption(meta["rule"])
            if msg.get("forecast") is not None:
                with st.expander("Forecast"):
                    st.dataframe(msg["forecast"], use_container_width=True)
            if msg.get("dashboard"):
                with st.expander("Generated dashboard specification"):
                    st.json(msg["dashboard"])
            if msg.get("tool_trace"):
                with st.expander("Agent tool trace"):
                    for item in msg["tool_trace"]:
                        st.write(f"Step {item['step']}: `{item['tool']}`")
                        st.json(item["arguments"])

    prompt = st.chat_input("Ask a question about your CSV data...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("AI analyst is reasoning and using tools..."):
                try:
                    result = run_agent(df, prompt, st.session_state.messages[:-1], stream_final=stream_final)
                    st.markdown(result["answer"])

                    if result.get("table") is not None:
                        st.dataframe(result["table"], use_container_width=True)
                    if result.get("chart") is not None:
                        st.plotly_chart(result["chart"], use_container_width=True)
                    if result.get("anomalies") is not None:
                        meta = result.get("anomaly_meta") or {}
                        count = int(meta.get("count", len(result["anomalies"])))
                        with st.expander("Anomaly detection", expanded=True):
                            if count:
                                st.warning(f"🚨 {count} anomal{"y" if count == 1 else "ies"} detected in `{meta.get("column", "numeric data")}`.")
                                st.dataframe(result["anomalies"], use_container_width=True)
                            else:
                                st.success(f"✅ No anomalies detected in `{meta.get("column", "the numeric data")}` using the {str(meta.get("method", "IQR")).upper()} method.")
                            if meta.get("rule"):
                                st.caption(meta["rule"])
                    if result.get("forecast") is not None:
                        with st.expander("Forecast"):
                            st.dataframe(result["forecast"], use_container_width=True)
                    if result.get("sql"):
                        with st.expander("Generated SQL"):
                            st.code(result["sql"], language="sql")
                    if result.get("code"):
                        with st.expander("Generated Pandas code"):
                            st.code(result["code"], language="python")
                    if result.get("dashboard"):
                        with st.expander("Generated dashboard"):
                            st.json(result["dashboard"])
                    with st.expander("Agent execution trace"):
                        for item in result.get("tool_trace", []):
                            st.write(f"Step {item['step']}: `{item['tool']}`")
                            st.json(item["arguments"])
                            if item.get("fallback"):
                                st.caption("Deterministic fallback used because the LLM was unavailable.")

                    st.session_state.last_result = result
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result["answer"],
                        "sql": result.get("sql"),
                        "code": result.get("code"),
                        "table": result.get("table"),
                        "chart": result.get("chart"),
                        "anomalies": result.get("anomalies"),
                        "anomaly_meta": result.get("anomaly_meta"),
                        "forecast": result.get("forecast"),
                        "dashboard": result.get("dashboard"),
                        "tool_trace": result.get("tool_trace"),
                    })
                except Exception as exc:
                    st.error(f"Analysis failed: {exc}")

with tab_export:
    st.subheader("Export")
    result = st.session_state.last_result
    if not result:
        st.info("Run an analysis first.")
    else:
        report = build_html_report(
            question=result.get("question", ""), answer=result.get("answer", ""),
            reasoning=result.get("reasoning", ""), sql=result.get("sql", ""),
            code=result.get("code", ""), plan=result.get("plan", {}),
            table=result.get("table"), anomalies=result.get("anomalies"),
            forecast=result.get("forecast"),
        )
        st.download_button("Download HTML report", report, f"ai_report_{datetime.now():%Y%m%d_%H%M%S}.html", "text/html", use_container_width=True)
        st.download_button("Download agent trace JSON", json.dumps(result.get("tool_trace", []), indent=2, default=str), "agent_trace.json", "application/json", use_container_width=True)
