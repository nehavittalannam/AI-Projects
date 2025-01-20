# Azure LlamaIndex SQL Query Engine with OpenAI LLM

This project demonstrates how to use Azure OpenAI's language model in combination with LlamaIndex to query SQL databases using natural language. The program sets up a connection to an SQL database, initializes a query engine with OpenAI's language model, and processes user queries through LlamaIndex.

## Prerequisites

Before running the project, make sure you have the following:

- Python 3.x
- Azure OpenAI API Key
- SQL Server Database (Azure or on-premise)
- The required Python packages (listed below)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/azure-llama-index-sql-query-engine.git
    cd azure-llama-index-sql-query-engine
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up environment variables for your OpenAI API:
    - `OPENAI_API_KEY`: Your OpenAI API key
    - `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint
    - `OPENAI_API_VERSION`: The API version you're using
    - Database connection details (SQL server username, password, database, etc.)

## LlamaIndex

This project uses [LlamaIndex](https://gpt-index.readthedocs.io/) to enable the querying of SQL databases using natural language. LlamaIndex facilitates the creation of a structured data query engine, allowing seamless interaction between the OpenAI LLM and SQL databases.

LlamaIndex helps transform SQL tables into easily queryable structures and ensures that your natural language queries are processed accurately by the LLM.

## Usage

1. Update the configuration with your database details and OpenAI API credentials.
2. Run the Python script to initialize the LLM, SQL database engine, and query engine:
    ```bash
    python llm_sql_query_engine.py
    ```

3. The program will process the queries and generate responses based on your SQL database.
