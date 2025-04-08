from dataclasses import dataclass

from src.config import KOMGA_API_KEY


@dataclass
class KomgaHeaders:
    GET = {
        'Accept': 'application/json',
        'X-API-Key': KOMGA_API_KEY
    }
    POST = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-API-Key': KOMGA_API_KEY
    }
    DEL = {
        'X-API-Key': KOMGA_API_KEY
    }
    PATCH = GET
    PUT = DEL
    ANALYZE = DEL
