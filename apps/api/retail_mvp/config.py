"""Server-only settings. Read local .env without overwriting process/Vercel settings."""
from dataclasses import dataclass, field
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]

def load_local_env() -> None:
    if os.getenv('VERCEL') or os.getenv('APP_ENV', 'local') != 'local':
        return
    path = ROOT / '.env'
    if path.exists():
        for line in path.read_text().splitlines():
            if '=' in line and not line.lstrip().startswith('#'):
                name, value = line.split('=', 1)
                if name.strip().isidentifier():
                    os.environ.setdefault(name.strip(), value.strip().strip('"').strip("'"))

load_local_env()

def flag(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).lower() == 'true'

def number(name: str, default: int, low: int, high: int) -> int:
    try:
        return max(low, min(high, int(os.getenv(name, str(default)))))
    except ValueError:
        return default

@dataclass(frozen=True)
class Settings:
    model: str
    api_key: str = field(repr=False)
    origins: tuple[str, ...]
    require_shared: bool
    redis_url: str
    redis_token: str = field(repr=False)
    salt: str = field(repr=False)
    rpm: int
    daily: int
    tokens_daily: int
    tokens_minute: int
    max_output: int
    timeout: int

    @classmethod
    def read(cls) -> 'Settings':
        deployed = bool(os.getenv('VERCEL')) or os.getenv('APP_ENV') == 'production'
        return cls(
            os.getenv('GROQ_MODEL', 'openai/gpt-oss-120b'), os.getenv('GROQ_API_KEY', ''),
            tuple(o.strip().rstrip('/') for o in os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',') if o.strip() and o.strip() != '*'),
            deployed or flag('REQUIRE_SHARED_LIMITER', False),
            os.getenv('UPSTASH_REDIS_REST_URL', '').rstrip('/'), os.getenv('UPSTASH_REDIS_REST_TOKEN', ''),
            os.getenv('RATE_LIMIT_SALT', ''), number('REQUESTS_PER_MINUTE', 8, 1, 30),
            number('GLOBAL_REQUESTS_PER_DAY', 150, 1, 1000),
            number('GLOBAL_TOKEN_RESERVATION_PER_DAY', 150000, 1000, 500000),
            number('GLOBAL_TOKEN_RESERVATION_PER_MINUTE', 24000, 1000, 100000),
            number('GROQ_MAX_OUTPUT_TOKENS', 900, 256, 1500), number('GROQ_TIMEOUT_SECONDS', 18, 5, 25),
        )
