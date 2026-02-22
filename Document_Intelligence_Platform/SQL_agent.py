from crewai.tools import tool
from crewai import Agent, Task, Crew, Process, LLM
import json
import pyodbc


# SQL Server connection configuration (Windows Authentication)
SQL_SERVER = 'your_sql_server'
SQL_DATABASE = 'your_database_name'

def get_sql_connection():
    """Get SQL Server connection using Windows Authentication"""
    try:
        connection_string = f'Driver={{ODBC Driver 17 for SQL Server}};Server={SQL_SERVER};Database={SQL_DATABASE};Trusted_Connection=yes'
        return pyodbc.connect(connection_string)
    except Exception as e:
        print(f"SQL Connection Error: {str(e)}")
        return None

def SQL_query_agent(table_name: str, column_details: str, user_query: str, context: str=""):
    llm = LLM(
        model="azure/your_model_name",
        api_version="your_api_version",
        base_url="your_azure_openai_base_url",
        api_key="your_azure_openai_api_key"
    )

    # Initialize SQL Server tool
    @tool
    def execute_sql_queries(queries: list) -> str:
        """
        Tool to connect to SQL Server and execute T-SQL queries.
        
        Args:
            queries: List of T-SQL query strings. Can contain one or multiple queries.
                    Each query should be a valid T-SQL statement.
                    Example: ["SELECT * FROM table WHERE age > 30", "SELECT COUNT(*) FROM table"]
            
        Returns:
            JSON string containing query results and execution status
        """
        try:
            conn = get_sql_connection()
            if not conn:
                return json.dumps({
                    'success': False,
                    'error': 'Failed to connect to SQL Server',
                    'results': []
                })
            
            cursor = conn.cursor()
            all_results = []
            
            for i, query in enumerate(queries):
                try:
                    cursor.execute(query)
                    
                    # Fetch results if it's a SELECT query
                    if query.strip().upper().startswith('SELECT'):
                        rows = cursor.fetchall()
                        columns = [description[0] for description in cursor.description] if cursor.description else []
                        
                        # Convert rows to list of dictionaries
                        result_data = []
                        for row in rows:
                            result_data.append(dict(zip(columns, row)))
                        
                        all_results.append({
                            'query_number': i + 1,
                            'query': query,
                            'success': True,
                            'row_count': len(result_data),
                            'columns': columns,
                            'data': result_data
                        })
                    else:
                        # For INSERT, UPDATE, DELETE queries
                        conn.commit()
                        all_results.append({
                            'query_number': i + 1,
                            'query': query,
                            'success': True,
                            'rows_affected': cursor.rowcount,
                            'message': f'Query executed successfully. Rows affected: {cursor.rowcount}'
                        })
                
                except Exception as e:
                    all_results.append({
                        'query_number': i + 1,
                        'query': query,
                        'success': False,
                        'error': str(e)
                    })
            
            cursor.close()
            conn.close()
            
            return json.dumps({
                'success': True,
                'total_queries': len(queries),
                'successful_queries': sum(1 for r in all_results if r.get('success', False)),
                'results': all_results
            }, indent=2, default=str)
        
        except Exception as e:
            return json.dumps({
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'results': []
            })
    
    # Build context section with previous conversation history
    context_text = ""
    if context:
        context_text = f"\n\nPrevious Conversation Context (use for understanding user intent and patterns):\n{context}\n"

    SQL_agent = Agent(
        role="T-SQL Query Generator",
        goal=(
           f'''Generate and execute valid T-SQL queries on SQL Server table "{table_name}" with columns: {column_details}
            to answer the user's query: "{user_query}".
            
            Provide clear, concise answers without mentioning table sources. Simply present the data directly.{context_text}'''
        ),
        backstory=f'''You are an expert T-SQL query specialist and data analysis expert. Your core responsibilities:
            
            1. Generate valid T-SQL queries based on user requirements
            2. Use execute_sql_queries tool to run the generated queries against SQL Server
            3. Analyze and synthesize query results
            4. Present findings clearly and professionally
            
            CRITICAL INSTRUCTIONS:
            - DO NOT mention which table the data came from
            - Simply provide the answer directly as if it's known information
            - No need to reference database, tables, or data sources
            
            CRITICAL QUERY GENERATION REQUIREMENTS:
            - Write only valid T-SQL syntax compatible with SQL Server
            - Use the exact table name: {table_name}
            - Available columns: {column_details}
            - For multiple queries needed, return them as a list: ["SELECT...", "SELECT...", "UPDATE..."]
            - For single query, return as single-item list: ["SELECT..."]
            - Always use column names exactly as provided (respect underscores and case)
            - Include proper WHERE clauses, JOINs, GROUP BY as needed
            - Handle NULL values appropriately
            - Use aggregate functions (COUNT, SUM, AVG, etc.) when needed
            - For text/string searches: Use LIKE '%smtg%' pattern for better wildcard matching results
            
            EXECUTION WORKFLOW:
            1. Analyze the user query carefully to understand data requirements
            2. Generate appropriate T-SQL query/queries to retrieve the needed data
            3. Return queries as a Python list of strings
            4. Use execute_sql_queries tool to execute the generated queries
            5. Analyze results and present findings in structured format
            
            OUTPUT STANDARDS:
            - Start directly with the answer (e.g., "Here are the findings:" or just present the data)
            - Use numbered points (1, 2, 3) to list findings
            - Include specific values and metrics from results
            - Maintain professional and conversational tone
            - Present data in easy-to-read format
            - No markdown or special characters in final output
            - NO mention of tables, databases, or data sources
            ''',
        tools=[execute_sql_queries],
        llm=llm,
        verbose=True,
    )

    task = Task(
        description=(
            f'''User Query: {user_query}
            Target Table: {table_name}
            Available Columns: {column_details}
            {context_text}
            
            TASK EXECUTION:
            1. Analyze user query to determine what data is needed
            2. Generate valid T-SQL query/queries to answer the user query
            3. Return queries as a list: ["QUERY1", "QUERY2"] or ["SINGLE_QUERY"]
            4. Use execute_sql_queries tool with the generated list of queries
            5. Analyze the results from the SQL execution
            6. Present findings in clear, professional format with numbered points WITHOUT mentioning table sources
            
            IMPORTANT - QUERY GENERATION RULES:
            - If one query is sufficient, generate ONE query in a list: ["SELECT * FROM {table_name} WHERE..."]
            - If multiple queries are needed, return all as list: ["SELECT...", "SELECT...", "UPDATE..."]
            - All queries MUST be valid T-SQL syntax
            - Use exact column names provided: {column_details}
            - Do NOT modify column names or add aliases that don't exist
            - For string/text searches: Use LIKE '%your_search_string%' pattern for more flexible and better matching results
            
            CRITICAL OUTPUT REQUIREMENT:
            - Do NOT mention the table name or any database references
            - Simply provide direct answers to the user query
            '''
        ),
        expected_output='''Response with:
        - Direct answer without mentioning table sources
        - Numbered point format (1, 2, 3, etc.) for findings
        - Specific data values from query results
        - Clear, professional language
        - Well-organized presentation
        - NO reference to tables or databases
        ''',
        agent=SQL_agent,
    )
    crew = Crew(
        agents=[SQL_agent],
        tasks=[task],
        process=Process.sequential,
    )
    result = crew.kickoff()
    output = result.raw

    return output
