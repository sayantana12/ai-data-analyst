# AI-Powered Data Analyst

An AI-powered data analysis application that allows users to upload CSV datasets and interact with their data using natural language.

The project combines LLM-based reasoning with analytical tools to perform data analysis, generate visualizations, detect anomalies, and generate SQL/Pandas code.

---

## Features

- CSV upload and validation
- Dataset profiling and data-quality checks
- Natural-language data analysis
- Business insights and summaries
- Automatic data visualization
- SQL generation
- Pandas code generation
- Anomaly detection
- Conversational context
- Forecasting support
- Semantic search support
- Dashboard generation support
- Local analytical fallback
- Docker support

---

## Project Flow

```text
CSV Upload
    ↓
Validation & Profiling
    ↓
User Natural-Language Question
    ↓
Agent / LLM Reasoning
    ↓
Analytical Tool Selection
    ↓
Pandas / SQL / Chart / Anomaly Analysis
    ↓
Actual Dataset Processing
    ↓
Result / Visualization / Code / Insight

Architecture
              User
               │
               ▼
        Streamlit Interface
               │
               ▼
          Agent Layer
               │
        ┌──────┴──────┐
        ▼             ▼
     LLM Layer    Local Fallback
        │             │
        └──────┬──────┘
               ▼
        Analytical Tools
               │
     ┌─────────┼─────────┐
     ▼         ▼         ▼
   Pandas     SQL      Charts
     │         │         │
     └─────────┼─────────┘
               ▼
          CSV Dataset

Detailed architecture diagram:
docs/architecture.svg
Project Structure
ai_data_analyst/
│
├── app.py
├── app/
│   └── core/
│       ├── agent.py          # Agent orchestration
│       ├── analytics.py      # Core analytics
│       ├── data_manager.py   # Dataset management
│       ├── llm.py            # LLM integration
│       ├── report.py         # Reporting
│       ├── search.py         # Semantic search
│       └── tools.py          # Analytical tools
│
├── data/                     # Sample datasets
├── docs/                     # Architecture diagram
├── tests/                    # Tests
├── eval/                     # Evaluation resources
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md

Technology Stack
- Python
- Streamlit
- Pandas
- DuckDB
- Plotly
- LLM API
- Docker
Setup
1. Clone
git clone https://github.com/sayantana12/ai-data-analyst.git
cd ai-data-analyst

2. Create environment
python -m venv .venv
.venv\Scripts\activate

3. Install dependencies
pip install -r requirements.txt

4. Configure API
Create a .env file using .env.example.
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=openrouter/free
APP_URL=http://localhost:8501
APP_NAME=AI Data Analyst

Do not commit .env or expose the API key.
5. Run
streamlit run app.py

Docker
Build and run:
docker compose up --build

Example Questions
Which region generated the highest revenue?

Show monthly sales trends.

What are the top five customers?

Detect anomalies in the dataset.

Generate SQL for this analysis.

Generate Pandas code for this analysis.

Current Status
The core data-analysis workflow is implemented, including CSV processing, natural-language analysis, analytical tools, visualization, anomaly detection, SQL/Pandas generation, conversational context, and fallback handling.
Some advanced features are still being refined, including robust  dashboard improvements, forecasting, authentication, report export, streaming, observability, and evaluation.
Note: With additional development time, the system could be further optimized for robustness, UI/UX, advanced analytics, and production readiness.