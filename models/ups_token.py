from dataclasses import dataclass
from typing import Optional

@dataclass
class UPSToken:
    access_token: str
    expires_in: str
    issued_at: Optional[str] = None
    token_type: Optional[str] = None
    client_id: Optional[str] = None
    scope: Optional[str] = None
    status: Optional[str] = None
    refresh_token: Optional[str] = None
    refresh_token_expires_in: Optional[str] = None
    refresh_token_status: Optional[str] = None
    refresh_token_issued_at: Optional[str] = None
    refresh_count: Optional[str] = None
