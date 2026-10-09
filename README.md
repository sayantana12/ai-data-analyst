# AI-Powered Data Analyst

A production-oriented Streamlit AI data analyst built for the Digital Back Office AI Engineer assignment.

The assignment requires an AI-powered analyst that accepts one or more CSV files, answers natural-language questions, generates insights and visualizations, detects anomalies, explains reasoning with an LLM, and maintains conversation context. The assignment also lists bonus capabilities including multi-file analysis, dashboard generation, data quality checks, forecasting, agentic workflows, tool calling and semantic search.

## What makes this an AI application rather than an LLM API wrapper?

Gemini is not used as a calculator or as a generic text generator. It is the **analyst/orchestrator**.

The agent receives the user's question, the dataset schema and conversation context. Gemini is given explicit function declarations for local analytics tools. It decides which tool to call, receives the computed result, evaluates that evidence, and can call another tool when the question requires multiple analytical steps. Only after the evidence is sufficient does it produce the final natural-language response and reasoning summary.

Flow:

```text
User question
    ↓
LLM Analyst Agent
    ├── understand intent
    ├── inspect schema/context
    ├── choose analytical tool(s)
    └── decide whether more evidence is needed
    ↓
Local tool execution
    ├── DuckDB SQL
    ├── safe Pandas operations
    ├── Plotly chart preparation
    ├── anomaly detection
    ├── forecasting
    ├── semantic search
    ├── data quality
    └── dashboard generation
    ↓
Tool result returned to LLM
    ↓
LLM evaluates evidence
    ↓
Optional additional tool call(s)
    ↓
Final answer + evidence-based reasoning summary
```

This is a genuine function-calling / agent loop. The application executes functions; Gemini only chooses and requests them. This follows the documented Gemini function-calling pattern: declare tools, let the model request a function, execute it in the application, send the function result back, and repeat as needed. See Google's official documentation: https://ai.google.dev/gemini-api/docs/function-calling

## Core requirement coverage

| Assignment requirement | Implementation |
|---|---|
| Upload and validate one or more CSV files | `data_manager.py` validates size, parseability, empty files and duplicate columns; multiple files are combined with a `_source_file` column. |
| Answer questions in natural language | Gemini Analyst Agent interprets the question and produces the final answer from tool evidence. |
| Generate business insights and summaries | LLM selects aggregation/search/SQL tools and explains computed findings. |
| Create charts | LLM calls `create_chart`; Plotly renders Bar, Line, Pie, Scatter and Histogram charts. |
| Generate SQL and/or Pandas code | LLM can call `execute_sql` or `generate_pandas_code`; generated Python is displayed, never executed. |
| Detect anomalies and explain why | LLM calls `detect_anomalies`; tool returns the exact IQR/z-score rule and flagged rows; LLM explains the evidence. |
| Explain reasoning | Final LLM response is instructed to provide a concise, auditable reasoning summary tied to tool results. |
| Maintain conversation context | Recent session messages are supplied to the LLM on every analytical turn. |

## Bonus coverage

### 1. Multi-file analysis

Multiple CSV uploads are validated and combined. Each row receives `_source_file`, preserving file provenance. The combined schema is passed to the analyst agent.

### 2. Dashboard generation

`create_dashboard` is an LLM-callable tool. It computes KPIs and creates dashboard widget specifications for category and monthly trends. The Streamlit Dashboard tab renders the returned specification.

### 3. Data quality checks

The quality tool reports row/column counts, missing cells, duplicate rows, data types, missing percentages and unique counts.

### 4. Forecasting

The `forecast` tool uses a transparent CPU-only linear trend over a date/time index. It requires at least three valid observations and returns future dates plus forecasts. It is explicitly presented as a simple trend forecast, not as a deep-learning model.

### 5. Agentic workflow

The agent runs a bounded multi-step loop (up to eight model/tool turns). Example:

```text
Question
  ↓
Tool call: aggregate revenue by region
  ↓
LLM receives result
  ↓
Tool call: filter winning region
  ↓
Tool call: rank products
  ↓
LLM evaluates evidence
  ↓
Final answer
```

### 6. Tool calling

Gemini receives real function declarations for the application's tools. Tool calls are parsed and executed by Python. Their results are returned to Gemini as function responses. No arbitrary Python is executed from the model.

### 7. Semantic search

`semantic_search` uses local TF-IDF vectorization and cosine similarity over row text. No second paid embedding service is required.

## Additional engineering features

The PDF also mentions other optional capabilities. The project includes or provides the following lightweight implementations where practical:

- Caching: Streamlit session state keeps conversation and last analysis results during the session.
- Authentication: optional password protection via `APP_PASSWORD`.
- Export reports: HTML report and agent trace JSON download.
- Streaming helper: the architecture is compatible with Gemini streaming; the final six-hour build prioritizes reliable function calling and evidence evaluation over a second streaming path.
- Observability/logging: every tool call is captured in the visible agent execution trace and exportable JSON.
- Evaluation framework: automated pytest tests cover core local analytical tools; the tool trace can be used for manual agent evaluation cases.

## Safety / production-minded decisions

- CSV input is validated before analysis.
- SQL execution is restricted to read-only `SELECT` / `WITH` statements.
- Mutating/external SQL keywords are rejected.
- Generated Pandas code is displayed but never executed.
- Tool arguments are validated against real dataframe columns.
- Tool errors are returned to the LLM so it can recover or explain missing information.
- The agent has a maximum number of tool-call steps to prevent infinite loops.
- The LLM is explicitly instructed not to invent data values or columns.
- The final answer is grounded in locally computed evidence.
- If the Gemini API is unavailable, a deterministic local fallback is used for common demo operations rather than fabricating an answer.

## Sample questions

- Which region generated the highest revenue?
- Show monthly sales trends.
- Which products are underperforming?
- What are the top five customers?
- Generate SQL for this analysis.
- Detect anomalies in the dataset.

## Setup

### 1. Create environment

Windows:

```powershell
python -m venv .venv
.venv\\Scripts\\activate
```

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install

```bash
pip install -r requirements.txt
```

### 3. Configure Gemini

Copy `.env.example` to `.env`:

```env
GEMINI_API_KEY=YOUR_FREE_GEMINI_API_KEY
GEMINI_MODEL=gemini-2.5-flash
APP_PASSWORD=
```

Do not commit `.env`.

### 4. Run

```bash
streamlit run app.py
```

## Docker

```bash
docker compose up --build
```

## Tests

```bash
pytest -q
```

## Architecture diagram

See `docs/architecture.svg`.

## Sample data

`data/sample_sales.csv` is included for the required demo questions.

## Submission evidence

The assignment requests screenshots and a 10–30 second demo video or live link. Those should be captured from the actually running application rather than fabricated. Add the resulting screenshots/video link to this README before submission.

## Implementation notes

1. Streamlit was selected for the six-hour implementation because it provides upload, chat, dashboard and export capabilities with a small frontend footprint.
2. Gemini is used as the reasoning/orchestration layer and function-calling interface.
3. DuckDB/Pandas/Plotly/scikit-learn perform deterministic local computation on CPU.
4. No GPU is required.
5. Forecasting is intentionally lightweight and transparent.
6. The project avoids arbitrary code execution from LLM output.
