import os
import sqlite3
import sqlite_vec
import hashlib
import google.generativeai as genai
from dotenv import load_dotenv

# --- CONFIG ---
load_dotenv(r'E:\0x\.env')
DB_PATH = r'E:\0x\agency\memory.db'
FILES_TO_INDEX = [
    r'E:\0x\Gemini.md',
    r'E:\0x\blueprints\G_CORE_IDENTITY.md',
    r'E:\0x\blueprints\KGF_v2.0_INGESTION.md',
    r'E:\0x\blueprints\SOUL_INGESTION.md'
]

# Set API Key
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

def get_embedding(text):
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=text,
        task_type="retrieval_document"
    )
    return result['embedding']

def chunk_text(text, chunk_size=1000, overlap=200):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += (chunk_size - overlap)
    return chunks

def index_files():
    conn = sqlite3.connect(DB_PATH)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    cursor = conn.cursor()

    print("--- BOOTSTRAP INDEXING START ---")

    for file_path in FILES_TO_INDEX:
        if not os.path.exists(file_path):
            print(f"Skipping: {file_path} (Not found)")
            continue

        print(f"Processing: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        file_hash = hashlib.md5(content.encode()).hexdigest()
        
        # Check if file changed
        cursor.execute("SELECT hash FROM files WHERE path=?", (file_path,))
        row = cursor.fetchone()
        if row and row[0] == file_hash:
            print(f"File unchanged: {file_path}")
            continue

        # Chunk and Embed
        chunks = chunk_text(content)
        cursor.execute("DELETE FROM chunks WHERE file_path=?", (file_path,))
        cursor.execute("INSERT OR REPLACE INTO files (path, hash) VALUES (?, ?)", (file_path, file_hash))

        for i, chunk in enumerate(chunks):
            chunk_id = f"{file_path}_{i}"
            embedding = get_embedding(chunk)
            
            # Store in standard table
            cursor.execute("INSERT INTO chunks (id, file_path, content) VALUES (?, ?, ?)", (chunk_id, file_path, chunk))
            
            # Store in vector table (using serialize_float32 for sqlite-vec)
            import struct
            # sqlite-vec expects a blob of float32
            blob = struct.pack(f'{len(embedding)}f', *embedding)
            cursor.execute("INSERT INTO chunks_vec(rowid, embedding) VALUES ((SELECT last_insert_rowid()), ?)", (blob,))
            
        print(f"Indexed {len(chunks)} chunks for {file_path}")

    conn.commit()
    conn.close()
    print("--- BOOTSTRAP INDEXING COMPLETE ---")
    print("BUILD SUCCESSFUL")

if __name__ == "__main__":
    index_files()
