from crewai.tools import tool
from crewai import Agent, Task, Crew, Process, LLM
from pydantic import BaseModel
from elasticsearch import Elasticsearch
import json
import re

def Document_query_agent(index_name: str, user_query: str, context: str=""):
    llm = LLM(
        model="azure/your_model_name",
        api_version="your_api_version",
        base_url="your_azure_openai_base_url",
        api_key="your_azure_openai_api_key"
    )

    # Initialize Elasticsearch connection
    @tool
    def elasticsearch_connection_tool(query: str, index_name: str) -> str:
        """
        Tool to connect to Elasticsearch and retrieve relevant document chunks from a specified index.
        Performs semantic search using vector embeddings.
        
        Args:
            query: User's search query
            index_name: Name of the Elasticsearch index to search
            
        Returns:
            JSON string containing relevant document chunks
        """
        try:
            es = Elasticsearch(
                hosts=["your_elasticsearch_host"],
                basic_auth=("your_elasticsearch_user", "your_elasticsearch_password"),
                ca_certs=r"your_ca_cert_path",
                verify_certs=True
            )
            
            # Perform search on the index
            search_body = {
                "size": 3,
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["text", "content"]
                    }
                }
            }
            
            response = es.search(index=index_name, body=search_body)
            
            # Extract and format chunks
            chunks = []
            for hit in response['hits']['hits']:
                source = hit['_source']
                chunks.append({
                    "content": source.get('text') or source.get('content', ''),
                    "score": hit['_score']
                })
            
            es.close()
            return json.dumps(chunks, indent=2)
        except Exception as e:
            return json.dumps({"error": f"Elasticsearch connection failed: {str(e)}"})
    
    # Build context section with previous conversation history
    context_text = ""
    if context:
        context_text = f"\n\nPrevious Conversation Context (use for understanding user intent and patterns):\n{context}\n"

    Document_agent = Agent(
        role="Document Search Specialist",
        goal=(
           f'''Retrieve and synthesize relevant information from document chunks stored in Elasticsearch index "{index_name}" 
            to answer the user's query: "{user_query}". 
            
            Provide clear, professional, concise responses without mentioning where the data came from.
            Simply present the information directly in a numbered pointer format.
            Focus on extracting the most relevant and accurate information from retrieved documents.
            Avoid generic responses and ensure all information directly addresses the user's query.{context_text}'''
        ),
        backstory=f'''You are an expert document analyst and information retrieval specialist. Your core responsibilities:
            
            1. Search and retrieve relevant document chunks from Elasticsearch
            2. Analyze retrieved content to answer queries accurately and comprehensively
            3. Synthesize information across multiple chunks when necessary
            4. Present findings in clean, professional, well-formatted manner
            
            CRITICAL INSTRUCTIONS:
            - DO NOT mention where the data came from or reference chunks/sources
            - Simply provide the answer directly to the user as if it's known information
            - Use numbered points (1, 2, 3, etc.) for all information lists
            - Maintain professional and conversational tone
            - Remove all special characters, markdown symbols, and code formatting
            - Ensure clarity, conciseness, and actionable content
            - No unnecessary technical jargon
            - Use proper spacing and logical grouping
            
            EXECUTION WORKFLOW:
            1. Use elasticsearch_connection_tool to retrieve document chunks from specified index
            2. Thoroughly analyze chunks for relevant context and relationships
            3. Extract information directly relevant to user query
            4. Present clean response without referencing data sources
            
            OUTPUT STANDARDS:
            - Start directly with the answer (e.g., "Here are the key points:" or just present the info)
            - Use numbered pointer format (1, 2, 3) for facts and findings
            - Include specific details without mentioning they came from documents
            - Maintain professional tone throughout
            - Zero markdown or special formatting
            - Clear structure with proper spacing and logical organization
            - NO justification or source attribution needed
            ''',
        tools=[elasticsearch_connection_tool],
        llm=llm,
        verbose=True,
    )

    task = Task(
        description=(
            f'''User Query: {user_query}
            Target Index: {index_name}
            Context from Previous Conversations:{context_text}
            
            TASK EXECUTION:
            1. Use elasticsearch_connection_tool to search for relevant document chunks in "{index_name}" index using the user query
            2. Analyze retrieved chunks carefully to extract most relevant information
            3. Synthesize findings from multiple chunks when necessary
            4. Present information directly without mentioning sources or chunks
            
            REQUIREMENTS:
            - Provide information directly addressing the user query
            - Do NOT mention where the data came from
            - Simply present the answer as direct information
            - Reference previous conversation context if relevant
            - Avoid generic or unfocused responses
            - Use conversational yet professional language
            - Clean output with no markdown or special characters
            '''
        ),
        expected_output='''Clear, concise response with:
        - Direct answer without source attribution (e.g., "Here are the key findings:")
        - Numbered point format (1, 2, 3, etc.) for information lists
        - Specific details presented directly without mentioning chunks
        - Clear, concise, actionable language
        - No markdown symbols, code fences, or special formatting
        - Well-structured with logical grouping and proper spacing
        - NO justification or explanation of where data came from
        ''',
        agent=Document_agent,
    )
    crew = Crew(
        agents=[Document_agent],
        tasks=[task],
        process=Process.sequential,
    )
    result=crew.kickoff()
    output=result.raw
    print("Raw Output:\n",output)

    return output
