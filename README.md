AI-Powered Data Analyst
An AI-powered data analysis application that allows users to upload CSV datasets and interact with their data using natural language.
The system combines an LLM-based reasoning layer with deterministic analytical tools to transform natural-language questions into useful data analysis, visualizations, anomaly detection results, and reproducible SQL/Pandas code.
Table of Contents
- Project Overview
- Problem Statement
- Objectives
- Key Features
- Project Flow
- System Architecture
- Folder Architecture
- Module Responsibilities
- Technology Stack
- Data Analysis Workflow
- LLM and Fallback Workflow
- Visualization Workflow
- Anomaly Detection Workflow
- SQL and Pandas Code Generation
- Conversation Context
- Setup and Installation
- Environment Variables
- Running the Application
- Docker Support
- Sample Dataset
- Example Questions
- Current Implementation Status
- Remaining Work
- Engineering Considerations
- Deliverables
- Future Improvements
Project Overview
The AI-Powered Data Analyst is designed to make data analysis accessible through natural-language interaction.
Instead of requiring the user to manually write SQL queries, Pandas operations, or visualization code, the user can upload a CSV dataset and ask questions such as:
Which region generated the highest revenue?

or:
Show the monthly sales trend.

The system interprets the request, selects the appropriate analytical operation, executes it against the uploaded dataset, and returns the result.
Depending on the request, the system can also generate:
- Business insights
- Charts
- SQL
- Pandas code
- Anomaly detection results
- Data-quality information
- Forecasting results
- Dashboard information
Problem Statement
Traditional data analysis requires knowledge of programming languages, SQL, statistical methods, and visualization libraries.
The objective of this project is to create an AI-assisted interface that allows users to interact with structured CSV data using natural language while keeping the actual analysis grounded in the uploaded dataset.
The application therefore combines:
Natural Language
       ↓
AI / Agent Reasoning
       ↓
Analytical Tool Selection
       ↓
Actual Dataset
       ↓
Computation
       ↓
Result / Chart / Code / Insight

Objectives
The project aims to provide:
- CSV upload and validation
- Natural-language data analysis
- Business insights and summaries
- Automatic visualization
- SQL generation
- Pandas code generation
- Anomaly detection
- Explanation of analytical results
- Conversational context
- Data-quality analysis
- Multi-file analysis capability
- Dashboard generation
- Forecasting support
- Semantic search support
- Modular and extensible architecture
- Local fallback for supported analytical operations
Key Features
1. CSV Upload and Validation
Users can upload CSV datasets through the Streamlit interface.
The system profiles the uploaded data and provides information such as:
- Number of rows
- Number of columns
- Column names
- Data types
- Missing values
- Duplicate records
- Dataset preview
2. Natural-Language Q&A
Users can ask questions about the uploaded dataset without manually writing code.
Example:
Which region generated the highest revenue?

The system interprets the question and performs the corresponding analysis.
3. Business Insights
The system can transform analytical results into understandable business-oriented responses.
Examples include:
- Highest-performing regions
- Top products
- Sales trends
- Customer performance
- Underperforming categories
- Summary statistics
4. Data Visualization
The application supports analytical visualizations based on the uploaded data.
Depending on the request and implementation, charts can include:
- Bar charts
- Line charts
- Pie charts
- Scatter plots
The visualization is generated from the actual dataset.
5. SQL Generation
The system can generate SQL for appropriate analytical questions.
Generated SQL is intended for read-only analytical operations.
Example:
Generate SQL for this analysis.

6. Pandas Code Generation
The system can generate Pandas code corresponding to supported analytical operations.
This provides users with reproducible code for the analysis.
Example:
Generate Pandas code for this analysis.

7. Anomaly Detection
The application includes anomaly-detection functionality for numerical data.
The system identifies records that deviate significantly from the expected distribution and returns the flagged records together with the detection method/rule.
8. Data Quality
The application provides data-quality information including:
- Missing cells
- Duplicate rows
- Column information
- Dataset dimensions
9. Forecasting
The analytical layer contains forecasting functionality for time-based numerical data.
The current forecasting implementation is intended as a baseline and can be extended with more advanced forecasting approaches.
10. Semantic Search
A semantic-search component is included to retrieve relevant records based on natural-language queries.
11. Dashboard Generation
The analytical tool layer contains dashboard-generation functionality capable of producing KPI information and analytical widgets.
The dashboard functionality can be extended further for fully automated multi-widget dashboards.
Project Flow
The complete application flow can be represented as follows:
                    USER
                      │
                      ▼
            ┌──────────────────┐
            │  Streamlit UI    │
            └────────┬─────────┘
                     │
                     ▼
            ┌──────────────────┐
            │ Upload CSV File  │
            └────────┬─────────┘
                     │
                     ▼
            ┌──────────────────┐
            │ Data Validation  │
            │ & Profiling      │
            └────────┬─────────┘
                     │
                     ▼
            ┌──────────────────┐
            │ Dataset Context  │
            └────────┬─────────┘
                     │
                     ▼
          ┌───────────────────────┐
          │ Natural Language      │
          │ User Question         │
          └───────────┬───────────┘
                      │
                      ▼
              ┌───────────────┐
              │ Agent / LLM   │
              │ Reasoning     │
              └───────┬───────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Select Tool /   │
             │ Analysis        │
             └───────┬─────────┘
                     │
       ┌─────────────┼─────────────┐
       │             │             │
       ▼             ▼             ▼
   Pandas/SQL     Chart       Anomaly
   Analysis       Creation   Detection
       │             │             │
       └─────────────┼─────────────┘
                     │
                     ▼
             ┌─────────────────┐
             │ Actual Dataset  │
             │ Computation     │
             └───────┬─────────┘
                     │
                     ▼
             ┌─────────────────┐
             │ Result / Chart  │
             │ / Code / Insight│
             └───────┬─────────┘
                     │
                     ▼
                   USER

System Architecture
The application follows a modular architecture.
                         ┌──────────────┐
                         │     User     │
                         └──────┬───────┘
                                │
                                ▼
                     ┌────────────────────┐
                     │    Streamlit UI    │
                     │      app.py        │
                     └─────────┬──────────┘
                               │
                               ▼
                     ┌────────────────────┐
                     │    Agent Layer     │
                     │     agent.py       │
                     └─────────┬──────────┘
                               │
                  ┌────────────┴────────────┐
                  │                         │
                  ▼                         ▼
          ┌───────────────┐       ┌────────────────┐
          │    LLM Layer  │       │ Local Fallback │
          │    llm.py     │       │   Analytics    │
          └───────┬───────┘       └───────┬────────┘
                  │                       │
                  └───────────┬───────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │    Tools Layer    │
                    │     tools.py      │
                    └─────────┬─────────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
            ▼                 ▼                 ▼
       ┌─────────┐       ┌─────────┐      ┌──────────┐
       │ Pandas  │       │   SQL   │      │ Charts   │
       └─────────┘       └─────────┘      └──────────┘
            │                 │                 │
            └─────────────────┼─────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Uploaded Dataset  │
                    │       CSV         │
                    └───────────────────┘

A visual version of the architecture is also provided in:
docs/architecture.svg

Folder Architecture
ai_data_analyst/
│
├── app.py
│
├── app/
│   └── core/
│       ├── __init__.py
│       ├── agent.py
│       ├── analytics.py
│       ├── data_manager.py
│       ├── llm.py
│       ├── report.py
│       ├── search.py
│       └── tools.py
│
├── data/
│   └── sample CSV dataset(s)
│
├── docs/
│   └── architecture.svg
│
├── tests/
│
├── eval/
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md

Module Responsibilities
app.py
Main Streamlit application.
Responsible for:
- User interface
- CSV upload
- Dataset display
- Chat interface
- Session/conversation state
- Displaying analytical results
- Rendering generated charts
app/core/agent.py
Agent orchestration layer.
Responsible for:
- Processing user requests
- Maintaining the analytical interaction flow
- Communicating with the LLM layer
- Selecting and executing analytical tools
- Handling tool results
- Returning the final response
- Handling fallback behaviour
app/core/llm.py
LLM integration layer.
Responsible for:
- LLM configuration
- System instructions
- Tool definitions
- Natural-language reasoning
- Structured analytical requests
- Communication with the configured LLM provider
app/core/analytics.py
Core analytical engine.
Contains functionality used for:
- SQL execution
- Anomaly detection
- Chart creation
- Forecasting
- Pandas code templates
- Safe column/identifier handling
- Analytical calculations
app/core/data_manager.py
Dataset-management layer.
Responsible for:
- Dataset profiling
- Data-quality analysis
- Dataset metadata
- Data validation-related functionality
app/core/tools.py
Tool execution layer.
Provides reusable analytical tools such as:
inspect_schema
generate_sql
execute_sql
run_pandas_analysis
create_chart
detect_anomalies
forecast
semantic_search
data_quality_check
create_dashboard
generate_pandas_code

The agent can use these tools to perform operations against the uploaded dataset.
app/core/search.py
Contains semantic-search functionality for retrieving relevant records from the dataset using a query.
app/core/report.py
Contains reporting-related functionality used by the application.
tests/
Contains project tests and is intended for validating individual components and analytical workflows.
eval/
Contains evaluation-related project resources and provides a foundation for evaluating analytical behaviour.
data/
Stores sample CSV dataset(s) used for testing and demonstration.
docs/
Contains project documentation assets.
Currently includes:
architecture.svg

Data Analysis Workflow
When a CSV is uploaded:
Step 1 — Upload
The user selects a CSV file through the Streamlit interface.
Step 2 — Load
The application loads the dataset into the data-processing layer.
Step 3 — Validate
Basic data-quality information is calculated.
Step 4 — Profile
The system identifies:
- Rows
- Columns
- Data types
- Missing values
- Duplicate records
Step 5 — Context
The dataset schema and relevant metadata become available to the analysis workflow.
Step 6 — User Question
The user asks a natural-language question.
Step 7 — Intent / Tool Selection
The agent determines what type of analysis is required.
Step 8 — Analytical Execution
The appropriate analytical tool operates on the actual dataset.
Step 9 — Result Processing
The result is converted into a user-readable response.
Step 10 — Visualization / Code
If requested or appropriate, the system can additionally produce:
- Charts
- SQL
- Pandas code
- Anomaly results
- Other analytical outputs
LLM and Fallback Workflow
The application is designed so that the LLM is not the only component capable of performing data analysis.
The conceptual workflow is:
User Question
      │
      ▼
LLM / Agent Reasoning
      │
      ▼
Analytical Tool
      │
      ▼
Actual CSV Data
      │
      ▼
Result

When external LLM processing is unavailable or fails for supported operations, the application can fall back to deterministic local analytical processing.
This improves reliability and reduces complete dependence on an external API.
Visualization Workflow
For a visualization request:
Natural-Language Question
          │
          ▼
      Agent / LLM
          │
          ▼
    Chart Parameters
          │
          ▼
     Chart Tool
          │
          ▼
     Actual Dataset
          │
          ▼
   Aggregation / Processing
          │
          ▼
      Plotly Chart
          │
          ▼
      Streamlit UI

The chart is generated using data from the uploaded dataset.
Anomaly Detection Workflow
User Request
     │
     ▼
Anomaly Detection Tool
     │
     ▼
Select Numerical Column
     │
     ▼
Statistical Detection
     │
     ▼
Flagged Records
     │
     ▼
Explanation / Result

The system can identify anomalous records and return information about the method/rule used.
SQL and Pandas Code Generation
The project supports reproducible analysis through generated code.
User Question
      │
      ▼
Analytical Interpretation
      │
      ├───────────────┐
      ▼               ▼
 Generate SQL     Generate Pandas
      │               │
      ▼               ▼
 Read-only SQL    Reproducible Python

This allows users to understand how an analysis can be reproduced outside the application.
Conversation Context
The application maintains conversational state during interaction.
For example:
User:
Which region generated the highest revenue?

Assistant:
Region X generated the highest revenue.

User:
What was its revenue?

Assistant:
...

The second question can be interpreted in the context of the previous interaction.
Technology Stack
Component	Technology
Programming Language	Python
User Interface	Streamlit
Data Processing	Pandas
SQL Analytics	DuckDB
Visualization	Plotly
LLM Integration	Configured LLM API
Containerization	Docker
Version Control	Git / GitHub


Setup and Installation
Prerequisites
Install:
- Python 3.x
- Git
- Docker (optional)
Clone Repository
git clone https://github.com/sayantana12/ai-data-analyst.git
cd ai-data-analyst

Create Virtual Environment
Windows
python -m venv .venv

Activate:
.venv\Scripts\activate

Install Dependencies
pip install -r requirements.txt

Environment Variables
Create a .env file in the project root.
Use .env.example as a template.
Example:
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=openrouter/free
APP_URL=http://localhost:8501
APP_NAME=AI Data Analyst

Never commit your actual .env file or API key.
Running the Application
After activating the virtual environment:
streamlit run app.py

The application will start on the local Streamlit server.
Docker Support
Docker configuration is provided through:
Dockerfile
docker-compose.yml

Run:
docker compose up --build

Docker support provides a reproducible environment for running the application.
Sample Dataset
Sample CSV dataset(s) are provided in:
data/

These datasets can be uploaded through the Streamlit application for testing.
The application is not limited to a fixed dataset and is designed to work with uploaded CSV data according to the supported analytical operations.
Example Questions
After uploading a suitable dataset, users can ask:
Which region generated the highest revenue?

Show monthly sales trends.

Which products are underperforming?

What are the top five customers?

Detect anomalies in the dataset.

Generate SQL for this analysis.

Generate Pandas code for this analysis.

Current Implementation Status
Implemented
The current project includes the core data-analysis workflow:
- CSV upload
- CSV validation
- Dataset profiling
- Data-quality checks
- Natural-language questions
- Analytical processing
- Business-oriented responses
- Visualization functionality
- SQL generation
- Pandas code generation
- Anomaly detection
- Conversational context
- Forecasting support
- Semantic-search support
- Dashboard-generation support
- Modular analytical tools
- LLM integration
- Local analytical fallback
- Docker configuration
- Sample dataset support
- Architecture documentation
Remaining / Under Refinement
The following capabilities from the complete assignment specification still require additional implementation, refinement, integration, or testing:
- More robust multi-file reasoning
- Automated dataset joining across multiple files
- More comprehensive automatic dashboard generation
- Forecasting improvements
- Semantic-search improvements
- Caching
- Authentication
- Report export
- Streaming responses
- Observability and logging
- Dedicated evaluation framework
- Further refinement of automatic analytical routing
- Further refinement of automatic visualization selection
These are designed as extensions to the current modular architecture.
Engineering Considerations
The application separates responsibilities across different modules rather than placing the entire workflow inside a single script.
The major layers are:
Presentation Layer
       ↓
Agent Layer
       ↓
LLM / Reasoning Layer
       ↓
Tool Layer
       ↓
Analytics Layer
       ↓
Dataset

This modular structure makes it possible to extend individual capabilities independently.
Examples:
- Add a new analytical tool without rewriting the UI.
- Replace or extend the LLM integration without rewriting the analytics engine.
- Add new visualization capabilities through the chart layer.
- Improve anomaly detection independently of the agent.
- Add new data sources in the future.
Error Handling and Reliability
The application is designed to handle failures at different stages of the workflow.
Examples include:
- Invalid CSV files
- Missing columns
- Unsupported analytical operations
- Invalid generated SQL
- External LLM/API failures
- Unsupported chart configurations
The local analytical layer provides a fallback for supported deterministic operations.
Security
API keys should be stored in environment variables.
The .env file must not be committed to GitHub.
The repository includes .gitignore configuration to prevent environment secrets and virtual-environment files from being uploaded.
Assignment Deliverables
The repository contains the requested project deliverables:
Complete Source Code
The complete application source code is included in the repository.
README
This document provides:
- Project overview
- Requirements
- Features
- Project flow
- Architecture
- Folder structure
- Setup instructions
- Usage instructions
- Current implementation status
Architecture Diagram
Available at:
docs/architecture.svg

Docker Support
Provided through:
Dockerfile
docker-compose.yml

Sample Dataset(s)
Provided in:
data/

Future Improvements
Future development can extend the project with:
- Advanced multi-dataset reasoning
- Automatic dataset relationships and joins
- More advanced forecasting models
- More intelligent visualization selection
- Automated report generation
- Downloadable analysis reports
- Authentication and user management
- Response streaming
- Caching of repeated analytical operations
- Production-grade logging and observability
- Automated evaluation benchmarks
- More sophisticated agentic workflows
- Additional data formats beyond CSV
Project Status
Core implementation completed with advanced capabilities under refinement.
The current version establishes the main pipeline required for an AI-powered data analyst:
CSV
 ↓
Validation
 ↓
Profiling
 ↓
Natural Language Question
 ↓
Agent / LLM
 ↓
Analytical Tool
 ↓
Actual Data Analysis
 ↓
Result / Chart / Code / Insight

The project is structured to allow the remaining advanced capabilities to be integrated incrementally without redesigning the core application.
Assignment
This project was developed as part of an AI/ML engineering assignment for an AI-powered Data Analyst system.