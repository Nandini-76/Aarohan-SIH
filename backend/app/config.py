# Memory Optimization Settings for Render Deployment
# These settings help reduce memory footprint for free tier hosting

# Chunk size for processing large datasets (rows at a time)
CHUNK_SIZE = 1000

# Maximum number of students to load in memory at once
MAX_STUDENTS_IN_MEMORY = 5000

# Whether to cache predictions in memory (disable on low memory)
ENABLE_PREDICTION_CACHE = False

# Log level (INFO for production, DEBUG for development)
LOG_LEVEL = "INFO"

# Whether to run preprocessing on startup (disable if data is pre-processed)
RUN_PREPROCESSING_ON_STARTUP = True

# Timeout for preprocessing operations (seconds)
PREPROCESSING_TIMEOUT = 600  # 10 minutes

# Whether to use compressed CSV for storage
USE_COMPRESSION = False

# Model loading settings
LAZY_LOAD_MODEL = False  # Load model only when needed

# Data retention settings
KEEP_INTERMEDIATE_FILES = False  # Delete cleaned_data.csv after predictions
