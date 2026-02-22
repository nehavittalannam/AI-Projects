from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch
from docling.document_converter import DocumentConverter
from pdf2docx import parse
import pandas as pd
import pyodbc
import os
import uuid
import re
from datetime import datetime
from SQL_agent import SQL_query_agent
from Document_agent import Document_query_agent

app = Flask(__name__)
CORS(app)

es = Elasticsearch(
    hosts=["your_elasticsearch_host"],
    basic_auth=("your_elasticsearch_user", "your_elasticsearch_password"),
    ca_certs=r"your_ca_cert_path",
    verify_certs=True
)

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# SQL Server connection configuration (Windows Authentication)
SQL_SERVER = 'your_sql_server'
SQL_DATABASE = 'your_database_name'

# Session management - store session data in memory
# Format: { session_id: { 'file_name': str, 'file_type': str, 'index_name': str, 'table_name': str, 
#                         'column_details': str, 'chat_history': [] } }
sessions = {}

def get_sql_connection():
    """Get SQL Server connection using Windows Authentication"""
    try:
        connection_string = f'Driver={{ODBC Driver 17 for SQL Server}};Server={SQL_SERVER};Database={SQL_DATABASE};Trusted_Connection=yes'
        return pyodbc.connect(connection_string)
    except Exception as e:
        print(f"SQL Connection Error: {str(e)}")
        return None

def extract_pdf(file_path):
    """Convert PDF to DOCX, then extract using Docling"""
    # Convert PDF to DOCX
    docx_path = file_path.replace('.pdf', '.docx')
    parse(file_path, docx_path, start=0, end=None)
    
    # Extract from converted DOCX using Docling
    converter = DocumentConverter()
    result = converter.convert(docx_path)
    markdown_content = result.document.export_to_markdown()
    
    # Clean up temporary DOCX file
    if os.path.exists(docx_path):
        os.remove(docx_path)
    
    return markdown_content

def extract_document(file_path):
    """Extract text from DOCX, PPTX, and other documents using Docling"""
    converter = DocumentConverter()
    result = converter.convert(file_path)
    markdown_content = result.document.export_to_markdown()
    return markdown_content

def extract_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def excel_to_sql(file_path, filename):
    """Convert Excel file to SQL Server table"""
    try:
        # Try multiple engines in order of likelihood
        df = None
        engines_to_try = ['openpyxl', 'xlrd', 'openpyxl']
        
        for engine in engines_to_try:
            try:
                df = pd.read_excel(file_path, engine=engine)
                print(f"Successfully read Excel file using engine: {engine}")
                break
            except Exception as e:
                print(f"Failed with engine {engine}: {str(e)}")
                continue
        
        if df is None:
            return None, "Cannot read Excel file. Ensure it's a valid .xlsx or .xls file."
        
        if df.empty:
            return None, "Excel file is empty"
        
        # Create table name from filename (remove extension and spaces)
        table_name = os.path.splitext(filename)[0]
        # Remove parentheses and their contents first
        table_name = re.sub(r'\s*\([^)]*\)\s*', '_', table_name)
        # Replace special characters with underscores
        table_name = table_name.replace(' ', '_').replace('-', '_').replace('.', '_').lower()
        # Remove multiple consecutive underscores
        table_name = re.sub(r'_+', '_', table_name)
        # Remove trailing underscores and numbers at the end if it looks like a version
        table_name = table_name.rstrip('_').rstrip('0123456789').rstrip('_')
        # Ensure table name starts with a letter (SQL Server requirement)
        if table_name and table_name[0].isdigit():
            table_name = 'tbl_' + table_name
        # Final cleanup - ensure it starts with a letter
        if not table_name or not table_name[0].isalpha():
            table_name = 'tbl_' + (table_name if table_name else 'data')
        
        # Get SQL connection
        conn = get_sql_connection()
        if not conn:
            return None, "Failed to connect to SQL Server"
        
        cursor = conn.cursor()
        
        # Drop table if it exists
        try:
            cursor.execute(f"DROP TABLE {table_name}")
            conn.commit()
            print(f"Dropped existing table: {table_name}")
        except:
            pass
        
        # Create column definitions
        columns_def = []
        for col in df.columns:
            col_name = col.replace(' ', '_').replace('-', '_').replace('.', '_')
            # Remove leading and trailing underscores
            col_name = col_name.strip('_')
            # Determine SQL data type based on pandas dtype
            if df[col].dtype == 'object':
                col_type = 'NVARCHAR(MAX)'
            elif df[col].dtype == 'int64':
                col_type = 'INT'
            elif df[col].dtype == 'float64':
                col_type = 'FLOAT'
            elif df[col].dtype == 'bool':
                col_type = 'BIT'
            else:
                col_type = 'NVARCHAR(MAX)'
            
            columns_def.append(f'{col_name} {col_type}')
        
        if not columns_def:
            return None, "No valid columns found in Excel file"
        
        # Create table
        create_table_sql = f"CREATE TABLE {table_name} ({', '.join(columns_def)})"
        cursor.execute(create_table_sql)
        conn.commit()
        print(f"Created table: {table_name}")
        
        # Insert data
        row_count = 0
        for index, row in df.iterrows():
            col_names = [col.replace(' ', '_').replace('-', '_').replace('.', '_').strip('_') for col in df.columns]
            placeholders = ', '.join(['?' for _ in col_names])
            col_names_str = ', '.join(col_names)
            
            insert_sql = f"INSERT INTO {table_name} ({col_names_str}) VALUES ({placeholders})"
            
            # Convert values, handling NaN
            values = [None if (isinstance(val, float) and pd.isna(val)) else str(val) if val is not None else None for val in row]
            cursor.execute(insert_sql, values)
            row_count += 1
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"Successfully inserted {row_count} rows into {table_name}")
        return table_name, None
    
    except Exception as e:
        print(f"Error in excel_to_sql: {str(e)}")
        return None, str(e)

def delete_old_indices():
    """Delete all existing indices before creating a new one"""
    try:
        # Get all indices, excluding system indices
        indices = es.indices.get(index="*", expand_wildcards="open")
        for index_name in indices.keys():
            # Skip system indices (starting with .) and skip .security* indices
            if not index_name.startswith('.'):
                es.indices.delete(index=index_name)
                print(f"Deleted index: {index_name}")
    except Exception as e:
        print(f"Error deleting indices: {str(e)}")

def create_index_and_store_embeddings(chunks, index_name):
    """Create Elasticsearch index and store chunks with embeddings"""
    try:
        # Generate embeddings for all chunks
        embeddings_data = []
        for i, chunk in enumerate(chunks):
            embedding = embedding_model.encode(chunk)
            embeddings_data.append({
                'text': chunk,
                'embedding': embedding.tolist(),
                'chunk_number': i + 1
            })
            print(f"Embedded chunk {i + 1}/{len(chunks)}")
        
        # Create index with mapping
        index_settings = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            "mappings": {
                "properties": {
                    "text": {"type": "text"},
                    "chunk_number": {"type": "integer"},
                    "embedding": {
                        "type": "dense_vector",
                        "dims": len(embeddings_data[0]['embedding']),
                        "index": True,
                        "similarity": "cosine"
                    }
                }
            }
        }
        
        # Create index
        es.indices.create(index=index_name, body=index_settings)
        print(f"Created index: {index_name}")
        
        # Index all documents
        for i, doc in enumerate(embeddings_data):
            es.index(
                index=index_name,
                id=i,
                body={
                    "text": doc['text'],
                    "chunk_number": doc['chunk_number'],
                    "embedding": doc['embedding']
                }
            )
        
        print(f"Successfully indexed {len(embeddings_data)} documents")
        return True
    except Exception as e:
        print(f"Error creating index and storing embeddings: {str(e)}")
        return False


@app.route('/')
def home():
    with open('home.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/chat')
def chat():
    with open('index.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/new-session', methods=['POST'])
def new_session():
    """Create a new session for a user"""
    try:
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            'file_name': None,
            'file_type': None,
            'index_name': None,
            'table_name': None,
            'column_details': None,
            'chat_history': []
        }
        return jsonify({'success': True, 'session_id': session_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/upload', methods=['POST'])
def upload():
    """Upload a file and process it for the current session"""
    try:
        session_id = request.form.get('session_id')
        if not session_id or session_id not in sessions:
            return jsonify({'success': False, 'error': 'Invalid session ID'})
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        file_ext = os.path.splitext(file.filename)[1].lower()
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        
        try:
            # Reset chat history for new file
            sessions[session_id]['chat_history'] = []
            sessions[session_id]['file_name'] = file.filename
            sessions[session_id]['file_type'] = file_ext
            
            # Handle Excel files
            if file_ext in ['.xlsx', '.xls']:
                table_name, error = excel_to_sql(file_path, file.filename)
                if error:
                    return jsonify({'success': False, 'error': error})
                
                # Get column details from the table
                col_details = get_table_columns(table_name)
                
                sessions[session_id]['table_name'] = table_name
                sessions[session_id]['column_details'] = col_details
                sessions[session_id]['index_name'] = None
                
                os.remove(file_path)
                
                return jsonify({
                    'success': True,
                    'file_type': 'excel',
                    'table_name': table_name,
                    'column_details': col_details,
                    'file_name': file.filename
                })
            
            # Handle document files (PDF, DOCX, PPTX, TXT)
            if file_ext == '.pdf':
                content = extract_pdf(file_path)
            elif file_ext in ['.docx', '.doc', '.pptx', '.ppt']:
                content = extract_document(file_path)
            elif file_ext == '.txt':
                content = extract_txt(file_path)
            else:
                return jsonify({'success': False, 'error': 'Unsupported file type'})
            
            # Split into chunks
            splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
            chunks = splitter.split_text(content)
            
            if not chunks:
                return jsonify({'success': False, 'error': 'No content extracted from file'})
            
            # Create unique index name for this session
            index_name = f"{session_id.split('-')[0]}_{os.path.splitext(file.filename)[0].lower().replace(' ', '_')}"
            
            # Create index and store embeddings
            success = create_index_and_store_embeddings(chunks, index_name)
            
            if not success:
                return jsonify({'success': False, 'error': 'Failed to store embeddings in Elasticsearch'})
            
            sessions[session_id]['index_name'] = index_name
            sessions[session_id]['column_details'] = None
            sessions[session_id]['table_name'] = None
            
            os.remove(file_path)
            
            return jsonify({
                'success': True,
                'file_type': 'document',
                'index_name': index_name,
                'total_chunks': len(chunks),
                'file_name': file.filename
            })
        
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({'success': False, 'error': str(e)})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/query', methods=['POST'])
def query():
    """Process a user query using the appropriate agent"""
    try:
        session_id = request.json.get('session_id')
        user_query = request.json.get('query')
        
        if not session_id or session_id not in sessions:
            return jsonify({'success': False, 'error': 'Invalid session ID'})
        
        if not user_query:
            return jsonify({'success': False, 'error': 'No query provided'})
        
        session_data = sessions[session_id]
        
        # Build context from last 5 chats
        context = build_context_from_history(session_data['chat_history'])
        
        try:
            # Determine which agent to use based on file type
            if session_data['table_name']:  # Excel file
                response = SQL_query_agent(
                    table_name=session_data['table_name'],
                    column_details=session_data['column_details'],
                    user_query=user_query,
                    context=context
                )
            elif session_data['index_name']:  # Document file
                response = Document_query_agent(
                    index_name=session_data['index_name'],
                    user_query=user_query,
                    context=context
                )
            else:
                return jsonify({'success': False, 'error': 'No file loaded in session'})
            
            # Add to chat history (keep last 5)
            session_data['chat_history'].append({
                'question': user_query,
                'answer': response,
                'timestamp': datetime.now().isoformat()
            })
            
            # Keep only last 5 messages
            if len(session_data['chat_history']) > 5:
                session_data['chat_history'] = session_data['chat_history'][-5:]
            
            return jsonify({
                'success': True,
                'response': response,
                'chat_history': session_data['chat_history']
            })
        
        except Exception as e:
            return jsonify({'success': False, 'error': f'Agent error: {str(e)}'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/session-info', methods=['GET'])
def session_info():
    """Get current session information"""
    try:
        session_id = request.args.get('session_id')
        
        if not session_id or session_id not in sessions:
            return jsonify({'success': False, 'error': 'Invalid session ID'})
        
        session_data = sessions[session_id]
        return jsonify({
            'success': True,
            'file_name': session_data['file_name'],
            'file_type': session_data['file_type'],
            'table_name': session_data['table_name'],
            'index_name': session_data['index_name'],
            'chat_count': len(session_data['chat_history'])
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def build_context_from_history(chat_history):
    """Build context string from chat history"""
    if not chat_history:
        return ""
    
    context_lines = []
    for chat in chat_history[-5:]:  # Last 5 chats
        context_lines.append(f"Q: {chat['question']}")
        context_lines.append(f"A: {chat['answer']}")
    
    return "\n".join(context_lines)

def get_table_columns(table_name):
    """Get column names and types from a SQL Server table"""
    try:
        conn = get_sql_connection()
        if not conn:
            return ""
        
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT COLUMN_NAME, DATA_TYPE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = '{table_name}'
            ORDER BY ORDINAL_POSITION
        """)
        
        columns = []
        for row in cursor.fetchall():
            columns.append(f"{row[0]} ({row[1]})")
        
        cursor.close()
        conn.close()
        
        return ", ".join(columns)
    except Exception as e:
        print(f"Error getting table columns: {str(e)}")
        return ""

@app.route('/extract', methods=['POST'])
def extract():
    """Legacy endpoint for backward compatibility"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        file_ext = os.path.splitext(file.filename)[1].lower()
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        
        try:
            # Handle Excel files
            if file_ext in ['.xlsx', '.xls']:
                table_name, error = excel_to_sql(file_path, file.filename)
                if error:
                    return jsonify({'success': False, 'error': error})
                
                # Clean up
                os.remove(file_path)
                
                return jsonify({
                    'success': True,
                    'table_name': table_name,
                    'message': f'Excel file successfully imported to table: {table_name}'
                })
            
            # Handle document files (PDF, DOCX, PPTX, TXT)
            if file_ext == '.pdf':
                content = extract_pdf(file_path)
            elif file_ext in ['.docx', '.doc', '.pptx', '.ppt']:
                content = extract_document(file_path)
            elif file_ext == '.txt':
                content = extract_txt(file_path)
            else:
                return jsonify({'success': False, 'error': 'Unsupported file type'})
            
            # Split into chunks
            splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
            chunks = splitter.split_text(content)
            
            if not chunks:
                return jsonify({'success': False, 'error': 'No content extracted from file'})
            
            # Delete old indices
            delete_old_indices()
            
            # Create index name from filename without extension
            index_name = os.path.splitext(file.filename)[0].lower().replace(' ', '_')
            
            # Create index and store embeddings
            success = create_index_and_store_embeddings(chunks, index_name)
            
            if not success:
                return jsonify({'success': False, 'error': 'Failed to store embeddings in Elasticsearch'})
            
            # Clean up
            os.remove(file_path)
            
            return jsonify({
                'success': True,
                'chunks': chunks,
                'index_name': index_name,
                'total_chunks': len(chunks),
                'embedding_dimension': 384
            })
        
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({'success': False, 'error': str(e)})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
