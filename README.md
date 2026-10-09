# 🤖 AI-Powered Data Analyst

An AI-powered data analysis application that allows users to upload CSV datasets and interact with their data using natural language.

The project combines LLM-based reasoning with analytical tools to perform data analysis, generate visualizations, detect anomalies, and generate SQL/Pandas code.

---

## ✨ Features

- 📂 CSV upload and validation
- 🔍 Dataset profiling and data-quality checks
- 💬 Natural-language data analysis
- 💡 Business insights and summaries
- 📊 Automatic data visualization
- 🗄️ SQL generation
- 🐼 Pandas code generation
- 🚨 Anomaly detection
- 🧠 Conversational context
- 📈 Forecasting support
- 🔎 Semantic search support
- 📊 Dashboard generation support
- 🔄 Local analytical fallback
- 🐳 Docker support

---

## 🔄 Project Flow

```text
CSV Upload
    ↓
Validation & Profiling
    ↓
Natural-Language Question
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

🏗️ System Architecture
                         User
                          │
                          ▼
                ┌──────────────────┐
                │ Streamlit UI     │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │   Agent Layer    │
                └────────┬─────────┘
                         │
                 ┌───────┴───────┐
                 ▼               ▼
          ┌────────────┐   ┌──────────────┐
          │ LLM Layer  │   │ Local        │
          │            │   │ Fallback     │
          └─────┬──────┘   └──────┬───────┘
                │                 │
                └────────┬────────┘
                         ▼
                ┌──────────────────┐
                │ Analytical Tools │
                └────────┬─────────┘
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
          ┌────────┐ ┌────────┐ ┌────────┐
          │ Pandas │ │  SQL   │ │ Charts │
          └────┬───┘ └────┬───┘ └────┬───┘
               │          │          │
               └──────────┼──────────┘
                          ▼
                  ┌──────────────┐
                  │ CSV Dataset  │
                  └──────────────┘

A detailed architecture diagram is also available at:
docs/architecture.svg

📁 Project Structure
ai_data_analyst/
│
├── app.py
│
├── app/
│   └── core/
│       ├── __init__.py
│       ├── agent.py          # Agent orchestration
│       ├── analytics.py      # Core analytics
│       ├── data_manager.py   # Dataset management
│       ├── llm.py            # LLM integration
│       ├── report.py         # Reporting
│       ├── search.py         # Semantic search
│       └── tools.py          # Analytical tools
│
├── data/                     # Sample datasets
├── docs/                     # Architecture documentation
├── tests/                    # Tests
├── eval/                     # Evaluation resources
│
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker configuration
├── docker-compose.yml        # Docker Compose configuration
├── .env.example              # Environment variable template
├── .gitignore
└── README.md

🛠️ Technology Stack
Component	Technology
Programming Language	Python
User Interface	Streamlit
Data Processing	Pandas
SQL Analytics	DuckDB
Visualization	Plotly
LLM Integration	LLM API
Containerization	Docker
Version Control	Git / GitHub

🚀 Setup
1. Clone the Repository
git clone https://github.com/sayantana12/ai-data-analyst.git
cd ai-data-analyst

2. Create a Virtual Environment
Windows:
python -m venv .venv
.venv\Scripts\activate

3. Install Dependencies
pip install -r requirements.txt

4. Configure the API
Create a .env file using .env.example as a reference.
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=openrouter/free
APP_URL=http://localhost:8501
APP_NAME=AI Data Analyst

⚠️ Important: Never commit your .env file or expose your API key publicly.

5. Run the Application
streamlit run app.py

🐳 Docker
Docker support is provided through:
- Dockerfile
- docker-compose.yml
Build and run the application with:
docker compose up --build

💬 Example Questions
After uploading a suitable dataset, users can ask:
Which region generated the highest revenue?

Show monthly sales trends.

What are the top five customers?

Which products are underperforming?

Detect anomalies in the dataset.

Generate SQL for this analysis.

Generate Pandas code for this analysis.

🧠 How It Works
The application follows a simple analytical workflow:
1. Upload a CSV dataset.
2. Validate and profile the dataset.
3. Ask a question in natural language.
4. The Agent/LLM layer interprets the request.
5. The appropriate analytical tool is selected.
6. The tool operates on the actual uploaded data.
7. The system returns a result, insight, visualization, anomaly report, or code.
8. Conversation context allows users to ask follow-up questions.
🛠️ Analytical Tools
The project provides modular tools for:
- Schema inspection
- SQL generation
- SQL execution
- Pandas analysis
- Chart creation
- Anomaly detection
- Forecasting
- Semantic search
- Data-quality checks
- Dashboard generation
- Pandas code generation
The modular design allows additional analytical capabilities to be added without restructuring the complete application.
🔄 LLM & Fallback Workflow
The system is designed so that supported analytical operations do not completely depend on an external LLM service.
Natural-Language Request
          ↓
     Agent / LLM
          ↓
   Analytical Tool
          ↓
    Actual Dataset
          ↓
 Result / Chart / Code

When external LLM processing is unavailable, supported deterministic operations can use the local analytical layer as a fallback.
📂 Sample Dataset
Sample CSV dataset(s) are provided in:
data/

These datasets can be uploaded through the application to test the analysis workflow.

📌 Current Status
✅ Core Implementation
The current implementation includes:
- CSV upload and validation
- Dataset profiling
- Natural-language analysis
- Business insights
- Data visualization
- SQL generation
- Pandas code generation
- Anomaly detection
- Conversational context
- Data-quality analysis
- Modular analytical tools
- LLM integration
- Local analytical fallback
- Docker support
🛠️ Under Refinement
Some advanced capabilities are still being refined or extended, including:
- Robust multi-file reasoning
- Dashboard improvements
- Forecasting improvements
- Semantic-search improvements
- Caching
- Authentication
- Report export
- Streaming responses
- Observability and logging
- Evaluation framework
Note: With additional development time, the system can be further optimized for robustness, UI/UX, advanced analytics, and production readiness.

📦 Assignment Deliverables
- ✅ Complete source code
- ✅ README with setup instructions
- ✅ Architecture diagram
- ✅ Docker support
- ✅ Sample dataset(s)

🔮 Future Improvements
Potential future improvements include:
- Advanced multi-file reasoning and dataset joins
- More sophisticated forecasting
- Automated report generation
- Downloadable analysis reports
- Authentication and user management
- Response streaming
- Caching
- Production-grade observability
- Automated evaluation
- More advanced agentic workflows