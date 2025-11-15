
import os

# Get the absolute path of the project root directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Define paths relative to the project root
DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'college_ai.db')
UPLOADS_DIR = os.path.join(PROJECT_ROOT, 'data', 'uploads')
CHROMA_DB_DIR = os.path.join(PROJECT_ROOT, 'data', 'chroma')

# Ensure the directories exist
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(CHROMA_DB_DIR, exist_ok=True)
