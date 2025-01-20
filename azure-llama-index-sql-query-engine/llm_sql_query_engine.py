import os
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.core import SQLDatabase
from llama_index.core.query_engine import NLSQLTableQueryEngine
from sqlalchemy import create_engine

os.environ["OPENAI_API_KEY"] = "your_api_key"
os.environ["AZURE_OPENAI_ENDPOINT"] = "end_point"
os.environ["OPENAI_API_VERSION"] = "api_version"

def initialize_llm():
    try:
        llm = AzureOpenAI(engine="deployment_name", model="model_name", temperature=0.0)
        print("Azure OpenAI model initialized successfully.")
        return llm
    except Exception as e:
        print(f"Error initializing LLM: {e}")
        raise

def create_db_engine():
    try:
        sqluser = "sql_user_name"
        sqlpassword = "sql_password"
        connection_string = f"mssql+pymssql://{sqluser}:{sqlpassword}@{'server_name'}/{'database_name'}"
        engine = create_engine(connection_string)
        print("Database engine created successfully.")
        return engine
    except Exception as e:
        print(f"Error creating database engine: {e}")
        raise

def initialize_sql_database(engine):
    try:
        sql_database = SQLDatabase(engine, include_tables=["table_name_1",
                                                           "tabl_name_2",
                                                           "...",
                                                           "table_name_n"
                                                            ])
        print("SQLDatabase initialized successfully.")
        return sql_database
    except Exception as e:
        print(f"Error initializing SQLDatabase: {e}")
        raise

def initialize_query_engine(sql_database, llm):
    try:
        query_engine = NLSQLTableQueryEngine(
            sql_database=sql_database, llm=llm
        )
        print("Query engine initialized successfully.")
        return query_engine
    except Exception as e:
        print(f"Error initializing query engine: {e}")
        raise

def process_user_query(query_str, query_engine):
    try:
        print(f"Processing user query: {query_str}")
        response = query_engine.query(query_str)
        print(f"Generated response: {response}")
        return response

    except Exception as e:
        print(f"Error processing user query: {e}")
        return "Sorry, there was an issue processing your request."

def main():
    llm = initialize_llm()
    engine = create_db_engine()
    sql_database = initialize_sql_database(engine)
    query_engine = initialize_query_engine(sql_database, llm)
    queries = [
        "please ask question on the tables in natural language"   
    ]
    for query in queries:
        response = process_user_query(query, query_engine)
        print(f"Response: {response}")  
        print(f"query:{query}")
        print(f"Response: {response}") 
        print("*"*50)
if __name__ == "__main__":
    main()
