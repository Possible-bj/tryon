from datetime import datetime

# Cohere API Configuration
COHERE_API_KEY = ""
EMBEDDING_MODEL = "embed-english-v3.0"  # Cohere model name
EMBEDDING_DIMENSION = 1024  # Dimension for Cohere embeddings

# FAISS Configuration
FAISS_INDEX_PATH = ""
METADATA_PATH = ""

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 5125

# Logging Configuration
CURRENT_TIME = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
CURRENT_USER = "tjc"