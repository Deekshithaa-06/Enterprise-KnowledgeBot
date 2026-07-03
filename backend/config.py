import os
from pathlib import Path
from dotenv import load_dotenv

# Load env variables from .env if present
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    PROJECT_NAME: str = "KnowledgeBot API"
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    DB_PATH: Path = BASE_DIR / "knowledge_bot.db"
    
    # We will prioritize env variable, then fall back to None
    @property
    def GEMINI_API_KEY(self) -> str:
        return os.environ.get("GEMINI_API_KEY", "")

    def set_api_key(self, api_key: str):
        # Update current process environment
        os.environ["GEMINI_API_KEY"] = api_key
        # Write to .env file to persist across restarts
        env_path = BASE_DIR / ".env"
        lines = []
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        
        # Replace or add GEMINI_API_KEY
        key_written = False
        new_lines = []
        for line in lines:
            if line.strip().startswith("GEMINI_API_KEY="):
                new_lines.append(f"GEMINI_API_KEY={api_key}\n")
                key_written = True
            else:
                new_lines.append(line)
        
        if not key_written:
            new_lines.append(f"GEMINI_API_KEY={api_key}\n")
            
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

settings = Settings()

# Ensure directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
