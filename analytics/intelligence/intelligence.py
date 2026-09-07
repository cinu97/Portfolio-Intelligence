from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Iterable

from analytics.intelligence.models import (
    Confidence,
    IntelligenceSignal,
    NewsEvidence,
    NewsItem,
    SignalDirection,
)
from analytics.intelligence.news import RSSNewsProvider
from analytics.intelligence.themes import themes_for_symbol


# ---------------------------------------------------------------------------
# Theme-specific directional phrases
# ---------------------------------------------------------------------------

THEME_DIRECTIONAL_PHRASES: dict[
    str,
    dict[str, tuple[tuple[str, str, int], ...]],
] = {

    # -----------------------------------------------------------------------
    # GOLD
    # -----------------------------------------------------------------------
    "gold": {
        "bullish": (
            ("gold prices rise to 3-month high", "STRONG", 5),
            ("gold prices rise to three-month high", "STRONG", 5),
            ("gold prices surge", "STRONG", 5),
            ("gold prices rally", "STRONG", 5),
            ("gold prices extend gains", "MODERATE", 3),
            ("gold prices edge higher", "MODERATE", 3),
            ("gold prices rise", "MODERATE", 3),
            ("gold price rises", "MODERATE", 3),
            ("gold gains", "MODERATE", 3),
            ("gold rises", "MODERATE", 3),
            ("gold demand rises", "MODERATE", 3),
            ("gold demand improves", "MODERATE", 3),
            ("strong gold demand", "MODERATE", 3),
            ("gold demand remains strong", "MODERATE", 3),
            ("central banks buy gold", "STRONG", 5),
        ),
        "bearish": (
            ("gold prices plunge", "STRONG", -5),
            ("gold prices crash", "STRONG", -5),
            ("gold prices fall", "STRONG", -5),
            ("gold prices decline", "STRONG", -5),
            ("gold prices drop", "STRONG", -5),
            ("gold price falls", "STRONG", -5),
            ("gold price drops", "STRONG", -5),
            ("gold drops", "STRONG", -5),
            ("gold falls", "STRONG", -5),
            ("gold demand weakens", "MODERATE", -3),
            ("gold demand falls", "MODERATE", -3),
            ("gold profit taking", "MODERATE", -3),
            ("gold profit-taking", "MODERATE", -3),
        ),
    },

    # -----------------------------------------------------------------------
    # BANKING
    # -----------------------------------------------------------------------
    "banking": {
        "bullish": (
            ("strong credit growth", "STRONG", 5),
            ("credit growth upward", "MODERATE", 3),
            ("credit growth cycle", "MODERATE", 3),
            ("bank credit growth", "MODERATE", 3),
            ("banking stocks gain", "MODERATE", 3),
            ("banking stocks rise", "MODERATE", 3),
            ("bank stocks gain", "MODERATE", 3),
            ("bank stocks rise", "MODERATE", 3),
            ("loan growth accelerates", "STRONG", 5),
            ("loan growth speeds up", "STRONG", 5),
            ("loan growth improves", "MODERATE", 3),
            ("bank credit expands", "MODERATE", 3),
            ("credit growth accelerates", "STRONG", 5),
        ),
        "bearish": (
            ("provisioning may hit profit", "MODERATE", -3),
            ("provisioning hits profit", "MODERATE", -3),
            ("provisioning pressure", "MODERATE", -3),
            ("credit growth slows", "STRONG", -5),
            ("credit growth weakens", "STRONG", -5),
            ("bank credit growth slows", "STRONG", -5),
            ("loan growth slows", "STRONG", -5),
            ("loan growth weakens", "STRONG", -5),
            ("banking stocks fall", "MODERATE", -3),
            ("bank stocks fall", "MODERATE", -3),
        ),
    },

    # -----------------------------------------------------------------------
    # IT SERVICES
    # -----------------------------------------------------------------------
    "it_services": {
        "bullish": (
            ("it services demand improves", "STRONG", 5),
            ("it services demand rises", "STRONG", 5),
            ("it services demand strengthens", "STRONG", 5),
            ("technology spending improves", "MODERATE", 3),
            ("technology spending rises", "MODERATE", 3),
            ("technology spending accelerates", "STRONG", 5),
            ("it spending improves", "MODERATE", 3),
            ("it spending rises", "MODERATE", 3),
            ("software demand improves", "MODERATE", 3),
            ("cloud demand improves", "MODERATE", 3),
            ("ai spending boosts", "MODERATE", 3),
        ),
        "bearish": (
            ("it services demand weakens", "STRONG", -5),
            ("it services demand falls", "STRONG", -5),
            ("technology spending slows", "STRONG", -5),
            ("technology spending falls", "STRONG", -5),
            ("it spending slows", "STRONG", -5),
            ("it spending falls", "STRONG", -5),
            ("software demand weakens", "MODERATE", -3),
            ("cloud spending slows", "MODERATE", -3),
            ("technology spending cuts", "STRONG", -5),
        ),
    },

    # -----------------------------------------------------------------------
    # FMCG
    # -----------------------------------------------------------------------
    "fmcg": {
        "bullish": (
            ("rural consumption boom", "STRONG", 5),
            ("rural consumption improves", "STRONG", 5),
            ("rural consumption rises", "STRONG", 5),
            ("rural consumption", "MODERATE", 3),
            ("rural demand recovery", "STRONG", 5),
            ("rural demand improves", "STRONG", 5),
            ("fmcg demand improves", "STRONG", 5),
            ("fmcg demand rises", "STRONG", 5),
            ("consumer demand improves", "MODERATE", 3),
            ("consumer demand rises", "MODERATE", 3),
            ("premium category growth", "MODERATE", 3),
            ("fmcg sales growth", "MODERATE", 3),
        ),
        "bearish": (
            ("rural consumption weakens", "STRONG", -5),
            ("rural consumption falls", "STRONG", -5),
            ("rural demand weakens", "STRONG", -5),
            ("rural demand falls", "STRONG", -5),
            ("fmcg demand weakens", "STRONG", -5),
            ("fmcg demand falls", "STRONG", -5),
            ("consumer demand weakens", "MODERATE", -3),
            ("consumer demand falls", "MODERATE", -3),
        ),
    },

    # -----------------------------------------------------------------------
    # DEFENCE
    # -----------------------------------------------------------------------
    "defence": {
        "bullish": (
            ("defence procurement", "STRONG", 5),
            ("defence procurement order", "STRONG", 5),
            ("defence order", "STRONG", 5),
            ("defence orders", "STRONG", 5),
            ("defence spending", "STRONG", 5),
            ("defence contract", "STRONG", 5),
            ("defence order win", "STRONG", 5),
            ("defence orders win", "STRONG", 5),
            ("defence production", "MODERATE", 3),
            ("defence exports rise", "MODERATE", 3),
        ),
        "bearish": (
            ("defence order delayed", "STRONG", -5),
            ("defence order delay", "STRONG", -5),
            ("defence budget cut", "STRONG", -5),
            ("defence order cancellation", "STRONG", -5),
            ("defence contract cancelled", "STRONG", -5),
            ("defence spending cut", "STRONG", -5),
        ),
    },

    # -----------------------------------------------------------------------
    # PHARMA
    # -----------------------------------------------------------------------
    "pharma": {
        "bullish": (
            ("fda approval", "STRONG", 5),
            ("us fda approval", "STRONG", 5),
            ("drug approval", "STRONG", 5),
            ("new drug approval", "STRONG", 5),
            ("drug receives approval", "STRONG", 5),
            ("pharma demand improves", "STRONG", 5),
            ("pharma demand rises", "STRONG", 5),
            ("drug demand improves", "MODERATE", 3),
            ("pharma exports rise", "MODERATE", 3),
        ),
        "bearish": (
            ("fda warning", "STRONG", -5),
            ("fda rejection", "STRONG", -5),
            ("fda inspection warning", "STRONG", -5),
            ("drug approval delayed", "MODERATE", -3),
            ("drug recall", "STRONG", -5),
            ("pharma demand weakens", "STRONG", -5),
            ("pharma demand falls", "STRONG", -5),
        ),
    },

    # -----------------------------------------------------------------------
    # OIL
    # -----------------------------------------------------------------------
    "oil": {
        "bullish": (
            ("crude oil prices rise", "STRONG", 5),
            ("crude oil prices surge", "STRONG", 5),
            ("oil prices rise", "STRONG", 5),
            ("oil prices surge", "STRONG", 5),
            ("oil prices edge higher", "MODERATE", 3),
            ("crude prices rise", "STRONG", 5),
            ("crude prices surge", "STRONG", 5),
        ),
        "bearish": (
            ("crude oil prices fall", "STRONG", -5),
            ("crude oil prices decline", "STRONG", -5),
            ("oil prices fall", "STRONG", -5),
            ("oil prices decline", "STRONG", -5),
            ("crude prices fall", "STRONG", -5),
            ("crude prices decline", "STRONG", -5),
        ),
    },

    # -----------------------------------------------------------------------
    # AUTOMOBILE
    # -----------------------------------------------------------------------
    "automobile": {
        "bullish": (
            ("strong demand growth", "STRONG", 5),
            ("auto demand growth", "STRONG", 5),
            ("vehicle sales rise", "STRONG", 5),
            ("vehicle sales surge", "STRONG", 5),
            ("auto demand surge", "STRONG", 5),
            ("automobile demand improves", "STRONG", 5),
            ("automobile demand rises", "STRONG", 5),
            ("auto sales rise", "STRONG", 5),
            ("auto sales growth", "MODERATE", 3),
            ("vehicle sales growth", "MODERATE", 3),
        ),
        "bearish": (
            ("automobile demand weakens", "STRONG", -5),
            ("automobile demand falls", "STRONG", -5),
            ("auto demand weakens", "STRONG", -5),
            ("auto demand falls", "STRONG", -5),
            ("vehicle sales fall", "STRONG", -5),
            ("vehicle sales decline", "STRONG", -5),
            ("auto sales fall", "STRONG", -5),
            ("auto sales decline", "STRONG", -5),
        ),
    },

    # -----------------------------------------------------------------------
    # METALS
    # -----------------------------------------------------------------------
    "metals": {
        "bullish": (
            ("metal prices rise", "STRONG", 5),
            ("metal prices surge", "STRONG", 5),
            ("steel prices rise", "STRONG", 5),
            ("copper prices rise", "STRONG", 5),
            ("aluminium prices rise", "STRONG", 5),
            ("metal demand improves", "MODERATE", 3),
            ("metal demand rises", "MODERATE", 3),
        ),
        "bearish": (
            ("metal prices fall", "STRONG", -5),
            ("metal prices decline", "STRONG", -5),
            ("steel prices fall", "STRONG", -5),
            ("copper prices fall", "STRONG", -5),
            ("aluminium prices fall", "STRONG", -5),
            ("metal demand weakens", "MODERATE", -3),
            ("metal demand falls", "MODERATE", -3),
        ),
    },
}


class NewsIntelligence:
    """
    Convert recent news into a conservative, explainable directional signal.

    Freshness:
        0-48 hours      = 100%
        48-96 hours     = 75%
        96-168 hours    = 50%
        >168 hours      = ignored

    Conflicting evidence is handled explicitly instead of being blindly
    summed together.
    """

    def __init__(
        self,
        provider: RSSNewsProvider | None = None,
        lookback_hours: int = 168,
    ) -> None:
        self.provider = provider or RSSNewsProvider()
        self.lookback_hours = lookback_hours

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def evaluate(
        self,
        symbol: str,
    ) -> IntelligenceSignal:

        themes = themes_for_symbol(symbol)

        all_news = self.provider.fetch(
            limit_per_feed=20,
        )

        recent_news = self._recent_news(
            all_news,
            self.lookback_hours,
        )

        evidence: list[NewsEvidence] = []

        for item in recent_news:

            evidence.extend(
                self._extract_evidence(
                    item,
                    themes,
                )
            )

        evidence = self._deduplicate_evidence(
            evidence
        )

        if not evidence:
            return IntelligenceSignal(
                direction=SignalDirection.NEUTRAL,
                confidence=Confidence.LOW,
                score=0,
                reasons=[
                    "No sufficiently specific recent "
                    "news evidence found"
                ],
                sources=[],
                evidence=[],
            )

        bullish_score = 0.0
        bearish_score = 0.0

        for item in evidence:

            news_item = self._find_news_item(
                recent_news,
                item.headline,
                item.source,
            )

            if news_item is None:
                continue

            multiplier = self._freshness_multiplier(
                news_item
            )

            weighted = (
                abs(item.score)
                * multiplier
            )

            if item.direction == SignalDirection.BULLISH:
                bullish_score += weighted

            elif item.direction == SignalDirection.BEARISH:
                bearish_score += weighted

        direction, score = self._resolve_direction(
            bullish_score,
            bearish_score,
        )

        confidence = self._confidence(
            evidence=evidence,
            direction=direction,
            bullish_score=bullish_score,
            bearish_score=bearish_score,
        )

        reasons = self._build_reasons(
            evidence,
            recent_news,
            direction,
        )

        sources = sorted(
            {
                item.source
                for item in evidence
            }
        )

        return IntelligenceSignal(
            direction=direction,
            confidence=confidence,
            score=score,
            reasons=reasons,
            sources=sources,
            evidence=evidence,
        )

    # -----------------------------------------------------------------------
    # Direction resolution
    # -----------------------------------------------------------------------

    @staticmethod
    def _resolve_direction(
        bullish_score: float,
        bearish_score: float,
    ) -> tuple[SignalDirection, int]:

        total = bullish_score + bearish_score

        if total <= 0:
            return SignalDirection.NEUTRAL, 0

        difference = bullish_score - bearish_score

        # Nearly balanced evidence = no directional signal.
        if abs(difference) < 1.5:
            return SignalDirection.NEUTRAL, 0

        # Mixed evidence must remain a weak signal.
        if bullish_score > 0 and bearish_score > 0:
            difference = max(
                -3,
                min(3, difference),
            )

        if difference > 0:
            return (
                SignalDirection.BULLISH,
                int(round(difference)),
            )

        return (
            SignalDirection.BEARISH,
            int(round(difference)),
        )

    # -----------------------------------------------------------------------
    # Evidence extraction
    # -----------------------------------------------------------------------

    def _extract_evidence(
        self,
        item: NewsItem,
        themes: tuple[str, ...],
    ) -> list[NewsEvidence]:

        text = (
            f"{item.title} {item.summary}"
        ).lower()

        results: list[NewsEvidence] = []

        for theme in themes:

            phrase_groups = (
                THEME_DIRECTIONAL_PHRASES.get(
                    theme,
                    {},
                )
            )

            bullish_matches: list[NewsEvidence] = []
            bearish_matches: list[NewsEvidence] = []

            for phrase, strength, score in phrase_groups.get(
                "bullish",
                (),
            ):

                if phrase.lower() in text:

                    bullish_matches.append(
                        NewsEvidence(
                            headline=item.title,
                            source=item.source,
                            theme=theme,
                            matched_phrase=phrase,
                            direction=SignalDirection.BULLISH,
                            strength=strength,
                            score=score,
                        )
                    )

            for phrase, strength, score in phrase_groups.get(
                "bearish",
                (),
            ):

                if phrase.lower() in text:

                    bearish_matches.append(
                        NewsEvidence(
                            headline=item.title,
                            source=item.source,
                            theme=theme,
                            matched_phrase=phrase,
                            direction=SignalDirection.BEARISH,
                            strength=strength,
                            score=score,
                        )
                    )

            # Keep the strongest phrase on each side.
            bullish = self._best_match(
                bullish_matches
            )

            bearish = self._best_match(
                bearish_matches
            )

            if bullish is not None and bearish is not None:

                # If the same headline contains both directions,
                # consider it ambiguous unless one side clearly dominates.
                if (
                    abs(bullish.score)
                    == abs(bearish.score)
                ):
                    continue

                if (
                    abs(bullish.score)
                    > abs(bearish.score)
                ):
                    results.append(bullish)
                else:
                    results.append(bearish)

            elif bullish is not None:

                results.append(bullish)

            elif bearish is not None:

                results.append(bearish)

        return results

    @staticmethod
    def _best_match(
        matches: list[NewsEvidence],
    ) -> NewsEvidence | None:

        if not matches:
            return None

        return max(
            matches,
            key=lambda item: (
                abs(item.score),
                len(item.matched_phrase),
            ),
        )

    # -----------------------------------------------------------------------
    # Freshness
    # -----------------------------------------------------------------------

    def _recent_news(
        self,
        news: Iterable[NewsItem],
        lookback_hours: int = 168,
    ) -> list[NewsItem]:

        now = datetime.now(
            timezone.utc
        )

        cutoff = now - timedelta(
            hours=lookback_hours
        )

        recent: list[NewsItem] = []

        for item in news:

            if item.published_at is None:
                continue

            published = item.published_at

            if published.tzinfo is None:
                published = published.replace(
                    tzinfo=timezone.utc
                )

            if (
                cutoff
                <= published
                <= now
            ):
                recent.append(item)

        return recent

    @staticmethod
    def _age_hours(
        item: NewsItem,
    ) -> float | None:

        if item.published_at is None:
            return None

        now = datetime.now(
            timezone.utc
        )

        published = item.published_at

        if published.tzinfo is None:
            published = published.replace(
                tzinfo=timezone.utc
            )

        age = (
            now - published
        ).total_seconds() / 3600

        return max(
            age,
            0.0,
        )

    def _freshness_multiplier(
        self,
        item: NewsItem,
    ) -> float:

        age = self._age_hours(
            item
        )

        if age is None:
            return 0.0

        if age <= 48:
            return 1.0

        if age <= 96:
            return 0.75

        if age <= 168:
            return 0.50

        return 0.0

    # -----------------------------------------------------------------------
    # Evidence cleanup
    # -----------------------------------------------------------------------

    @staticmethod
    def _deduplicate_evidence(
        evidence: list[NewsEvidence],
    ) -> list[NewsEvidence]:

        seen: set[
            tuple[str, str, str, str]
        ] = set()

        result: list[NewsEvidence] = []

        for item in evidence:

            key = (
                item.headline.strip().lower(),
                item.source.strip().lower(),
                item.theme,
                item.direction.value,
            )

            if key in seen:
                continue

            seen.add(key)
            result.append(item)

        return result

    @staticmethod
    def _find_news_item(
        news: list[NewsItem],
        headline: str,
        source: str,
    ) -> NewsItem | None:

        headline_key = (
            headline.strip().lower()
        )

        source_key = (
            source.strip().lower()
        )

        for item in news:

            if (
                item.title.strip().lower()
                == headline_key
                and item.source.strip().lower()
                == source_key
            ):
                return item

        return None

    # -----------------------------------------------------------------------
    # Confidence
    # -----------------------------------------------------------------------

    @staticmethod
    def _confidence(
        evidence: list[NewsEvidence],
        direction: SignalDirection,
        bullish_score: float,
        bearish_score: float,
    ) -> Confidence:

        if direction == SignalDirection.NEUTRAL:
            return Confidence.LOW

        dominant = max(
            bullish_score,
            bearish_score,
        )

        weaker = min(
            bullish_score,
            bearish_score,
        )

        strong_count = sum(
            1
            for item in evidence
            if item.strength == "STRONG"
        )

        # Mixed evidence: never HIGH confidence.
        if weaker > 0:
            return (
                Confidence.MEDIUM
                if dominant >= 4
                else Confidence.LOW
            )

        if (
            strong_count >= 2
            and dominant >= 5
        ):
            return Confidence.HIGH

        if (
            strong_count >= 1
            and dominant >= 3
        ):
            return Confidence.MEDIUM

        if len(evidence) >= 2:
            return Confidence.MEDIUM

        return Confidence.LOW

    # -----------------------------------------------------------------------
    # Decision trace
    # -----------------------------------------------------------------------

    def _build_reasons(
        self,
        evidence: list[NewsEvidence],
        recent_news: list[NewsItem],
        direction: SignalDirection,
    ) -> list[str]:

        reasons: list[str] = []

        for item in evidence[:5]:

            news_item = self._find_news_item(
                recent_news,
                item.headline,
                item.source,
            )

            if news_item is None:
                continue

            multiplier = self._freshness_multiplier(
                news_item
            )

            weighted_score = int(
                round(
                    abs(item.score)
                    * multiplier
                )
            )

            if weighted_score <= 0:
                continue

            reasons.append(
                f"{item.direction.value}: "
                f"{item.matched_phrase} "
                f"[{item.theme}, "
                f"{item.strength}, "
                f"{item.source}]"
            )

        if (
            direction != SignalDirection.NEUTRAL
            and any(
                item.direction != direction
                for item in evidence
            )
        ):
            reasons.append(
                "Mixed directional evidence; "
                "signal strength capped"
            )

        if not reasons:
            reasons.append(
                "Recent evidence exists but has "
                "insufficient weighted impact"
            )

        return reasons