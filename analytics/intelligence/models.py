from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class SignalDirection(str, Enum):
    BULLISH = "BULLISH"
    NEUTRAL = "NEUTRAL"
    BEARISH = "BEARISH"


class Confidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass(slots=True)
class InstrumentMetadata:
    symbol: str
    yahoo_symbol: str
    instrument_type: str
    provider: str = ""
    underlying_index: str = ""
    primary_theme: str = "unknown"
    themes: tuple[str, ...] = ()
    asset_class: str = ""
    inav_provider: str = ""
    news_search_terms: tuple[str, ...] = ()
    news_themes: tuple[str, ...] = ()
    geographic_exposure: str = ""


@dataclass(slots=True)
class NewsItem:
    title: str
    source: str
    url: str
    published_at: datetime | None
    summary: str = ""
    themes: tuple[str, ...] = ()
    symbol: str = ""
    direction: SignalDirection | None = None
    strength: str = ""
    confidence: Confidence | None = None
    reason: str = ""
    search_term: str = ""


@dataclass(slots=True)
class NewsEvidence:
    """One explainable piece of directional news evidence."""

    headline: str
    source: str
    theme: str
    matched_phrase: str
    direction: SignalDirection
    strength: str
    score: int
    symbol: str = ""
    published_at: datetime | None = None
    search_term: str = ""
    reason: str = ""


@dataclass(slots=True)
class IntelligenceSignal:
    direction: SignalDirection
    confidence: Confidence
    score: int
    reasons: list[str]
    sources: list[str]
    evidence: list[NewsEvidence]
    symbol: str = ""
    news_score: int = 0
    confidence_value: int = 0
    raw_evidence: list[NewsEvidence] = field(default_factory=list)