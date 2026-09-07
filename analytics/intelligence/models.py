from __future__ import annotations

from dataclasses import dataclass
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
class NewsItem:
    title: str
    source: str
    url: str
    published_at: datetime | None
    summary: str = ""
    themes: tuple[str, ...] = ()


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


@dataclass(slots=True)
class IntelligenceSignal:
    direction: SignalDirection
    confidence: Confidence
    score: int
    reasons: list[str]
    sources: list[str]
    evidence: list[NewsEvidence]