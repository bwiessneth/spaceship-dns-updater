from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Record(BaseModel):
    type: str
    name: str
    ttl: int = Field(..., ge=60, le=3600, description="TTL must be between 60 and 3600")


class DomainConfig(BaseModel):
    records: List[Record]


class ConfigModel(BaseModel):
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    domains: Dict[str, DomainConfig]
