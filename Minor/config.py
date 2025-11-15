import os

# Get the absolute path of the project root directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Define paths relative to the project root
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
DB_PATH = os.path.join(DATA_DIR, 'college_ai.db')
UPLOADS_DIR = os.path.join(DATA_DIR, 'uploads')
CHROMA_DB_DIR = os.path.join(DATA_DIR, 'chroma')

# Ensure the directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(CHROMA_DB_DIR, exist_ok=True)

print(f"✅ Config initialized:")
print(f"   DB: {DB_PATH}")
print(f"   Uploads: {UPLOADS_DIR}")
print(f"   ChromaDB: {CHROMA_DB_DIR}")