from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


NewsStatus = Literal["ok", "empty", "not_configured", "unavailable", "rate_limited"]


class ProviderSentiment(BaseModel):
    label: str
    score: float | None = Field(default=None, allow_inf_nan=False)


class TickerAssociation(BaseModel):
    ticker: str
    relevance: float | None = Field(default=None, ge=0, le=1, allow_inf_nan=False)
    sentiment: ProviderSentiment | None = None


class NewsCandidate(BaseModel):
    """Provider-independent adapter output; the service owns article selection."""
    title: str
    source: str
    published_at: datetime
    url: HttpUrl
    summary: str | None = None
    topics: list[str] = Field(default_factory=list)
    associations: list[TickerAssociation] = Field(default_factory=list)
    provider_id: str | None = None
    company_names: list[str] = Field(default_factory=list)


class NewsArticle(BaseModel):
    title: str
    source: str
    published_at: datetime
    url: HttpUrl
    summary: str | None = None
    topics: list[str] = Field(default_factory=list)
    provider_sentiment: ProviderSentiment | None = None
    why_it_may_matter: str | None = None
    match_reason: str


class NewsResponse(BaseModel):
    ticker: str
    retrieved_at: datetime
    status: NewsStatus
    message: str | None = None
    articles: list[NewsArticle] = Field(default_factory=list, max_length=4)
    provider: str
    cache_ttl_seconds: int = 600
    selection_note: str = "Company named in headline · selected publications · past seven days"
