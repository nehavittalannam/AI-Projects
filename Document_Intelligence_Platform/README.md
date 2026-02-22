# Document Intelligence Assistant

A powerful document and data query system that leverages AI agents to extract insights from documents and SQL databases.

## Features

- **Document Analysis**: Upload and query PDF, DOCX, PPTX, TXT, and Excel files
- **SQL Database Integration**: Analyze data stored in SQL Server databases
- **Vector Search**: Semantic search using Elasticsearch with embeddings
- **Multi-Agent System**: Specialized agents for document and SQL queries
- **Session Management**: Maintain conversation context across multiple queries

## Prerequisites

- Python 3.8+
- Elasticsearch 9.2.4+
- SQL Server with ODBC Driver 17
- Azure OpenAI Account (for LLM)

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Required Credentials

Add the following to your environment or update the configuration files:

#### 1. **LLM Credentials (Azure OpenAI)**
Update the LLM configuration in `SQL_agent.py` and `Document_agent.py`:
```python
llm = LLM(
    model="azure/gpt-4o",
    api_version="YOUR_API_VERSION",
    base_url="YOUR_AZURE_OPENAI_BASE_URL",
    api_key="YOUR_AZURE_OPENAI_API_KEY"
)
```

#### 2. **Elasticsearch Credentials**
Update the Elasticsearch connection in `app.py` and `Document_agent.py`:
```python
es = Elasticsearch(
    hosts=["https://localhost:9200"],
    basic_auth=("YOUR_ELASTIC_USERNAME", "YOUR_ELASTIC_PASSWORD"),
    ca_certs=r"PATH_TO_HTTP_CA.CRT",
    verify_certs=True
)
```

#### 3. **SQL Server Database Connection**
Update the SQL Server configuration in `app.py` and `SQL_agent.py`:
```python
SQL_SERVER = 'YOUR_SQL_SERVER_HOST'
SQL_DATABASE = 'YOUR_DATABASE_NAME'
# Connection string uses Windows Authentication by default
connection_string = f'Driver={{ODBC Driver 17 for SQL Server}};Server={SQL_SERVER};Database={SQL_DATABASE};Trusted_Connection=yes'
```

## Running the Application

Start the Flask server:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

- Home page: `http://localhost:5000/`
- Chat interface: `http://localhost:5000/chat`

## API Endpoints

- **POST** `/new-session` - Create a new chat session
- **POST** `/upload` - Upload a file for analysis
- **POST** `/query` - Submit a query to the agents
- **GET** `/session-info` - Get current session information

## File Structure

```
.
├── app.py                 # Main Flask application
├── SQL_agent.py          # SQL query agent using CrewAI
├── Document_agent.py     # Document search agent using CrewAI
├── index.html            # Chat interface
├── home.html             # Home page
├── requirements.txt      # Python dependencies
└── uploads/              # Uploaded files directory
```

## Supported File Types

- PDF (.pdf)
- DOCX (.docx, .doc)
- PPTX (.pptx, .ppt)
- Excel (.xlsx, .xls)
- Text (.txt)

## Notes

- Ensure Elasticsearch is running and accessible
- Verify SQL Server connection and database exists
- Update API keys and credentials before running the application
- Files are temporarily stored in the `uploads/` folder during processing
