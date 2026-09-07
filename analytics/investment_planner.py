from __future__ import annotations

from dataclasses import dataclass
from math import floor

from analytics.intelligence.themes import themes_for_symbol


@dataclass(slots=True)
class InvestmentPlan:
    symbol: str
    amount: int
    score: int
    reason: str
    quantity: int = 0
    price: float = 0.0
    target_allocation_percent: float = 0.0
    current_allocation_percent: float = 0.0
    allocation_gap_amount: int = 0


class InvestmentPlanner:
    """
    Portfolio-aware capital allocator.

    Uses:
    - monthly investment budget
    - portfolio allocation gap
    - aggregate theme exposure
    - recommendation conviction
    - actual ETF price
    - theme overlap protection

    The planner first evaluates portfolio-level theme exposure,
    then selects the highest-conviction instrument within each theme.
    """

    DEFAULT_TARGET_ALLOCATION = 5.0
    DEFAULT_RESERVE_PERCENT = 0.0
    DEFAULT_MAX_POSITIONS = 5

    PRIMARY_THEMES = {
        "banking",
        "it_services",
        "technology",
        "pharma",
        "healthcare",
        "fmcg",
        "defence",
        "metals",
        "commodities",
        "oil",
        "energy",
        "gold",
        "silver",
        "reit",
        "real_estate",
        "psu",
        "automobile",
        "nifty",
        "nifty_next_50",
        "mid_cap",
        "small_cap",
        "sensex",
        "financials",
        "financial_market",
        "value",
        "dividend",
        "cash",
        "liquid",
        "internet",
    }

    @classmethod
    def _primary_theme(cls, symbol: str) -> str:
        """Return the primary configured investment theme."""

        themes = themes_for_symbol(symbol)

        for theme in themes:
            if theme in cls.PRIMARY_THEMES:
                return theme

        return themes[0] if themes else "unknown"

    @classmethod
    def _build_theme_exposure(
        cls,
        contexts,
    ) -> dict[str, float]:
        """
        Calculate existing portfolio allocation by primary theme.

        Example:

            GOLDCASE   4%
            GOLDBEES   3%
            GOLDIETF   2%

        becomes:

            gold = 9%
        """

        theme_exposure: dict[str, float] = {}

        for context in contexts.values():

            symbol = context.symbol

            theme = cls._primary_theme(symbol)

            allocation = float(
                getattr(
                    context,
                    "allocation_percent",
                    0.0,
                )
                or 0.0
            )

            theme_exposure[theme] = (
                theme_exposure.get(theme, 0.0)
                + allocation
            )

        return theme_exposure

    @classmethod
    def _deduplicate_themes(
        cls,
        candidates: list[dict],
    ) -> list[dict]:
        """
        Keep only the highest-conviction candidate for each theme.

        Candidates must already be sorted by score descending.
        """

        selected: list[dict] = []
        used_themes: set[str] = set()

        for item in candidates:

            symbol = item["market"].symbol

            theme = cls._primary_theme(symbol)

            if theme in used_themes:
                continue

            item["primary_theme"] = theme

            used_themes.add(theme)

            selected.append(item)

        return selected

    @classmethod
    def create_plan(
        cls,
        recommendations,
        contexts,
        available_cash: int,
        target_allocation_percent: float = DEFAULT_TARGET_ALLOCATION,
        reserve_cash_percent: float = DEFAULT_RESERVE_PERCENT,
        max_positions: int = DEFAULT_MAX_POSITIONS,
    ) -> list[InvestmentPlan]:

        if available_cash <= 0:
            return []

        investable_cash = int(
            available_cash
            * (1 - reserve_cash_percent / 100)
        )

        if investable_cash <= 0:
            return []

        # ---------------------------------------------------------------
        # Build portfolio-level theme exposure.
        # ---------------------------------------------------------------
        theme_exposure = cls._build_theme_exposure(
            contexts
        )

        candidates = []

        for item in recommendations:

            market, recommendation = item

            context = contexts.get(
                market.symbol
            )

            if context is None:
                continue

            if recommendation.action not in {
                "BUY",
                "ACCUMULATE",
            }:
                continue

            price = float(
                getattr(
                    market,
                    "live_price",
                    0,
                )
                or 0
            )

            if price <= 0:
                continue

            symbol = market.symbol

            primary_theme = cls._primary_theme(
                symbol
            )

            # -----------------------------------------------------------
            # Individual instrument allocation.
            # -----------------------------------------------------------
            current_allocation = float(
                getattr(
                    context,
                    "allocation_percent",
                    0.0,
                )
                or 0.0
            )

            allocation_gap_percent = max(
                target_allocation_percent
                - current_allocation,
                0,
            )

            if allocation_gap_percent <= 0:
                continue

            # -----------------------------------------------------------
            # Aggregate theme allocation.
            #
            # Example:
            # GOLDCASE 4%
            # GOLDIETF 3%
            # GOLDBEES 2%
            #
            # Gold exposure = 9%
            #
            # Therefore a new gold investment is restricted.
            # -----------------------------------------------------------
            current_theme_allocation = (
                theme_exposure.get(
                    primary_theme,
                    0.0,
                )
            )

            theme_gap_percent = max(
                target_allocation_percent
                - current_theme_allocation,
                0,
            )

            # If the theme already exceeds the target,
            # don't allocate additional money to it.
            if theme_gap_percent <= 0:
                continue

            current_value = float(
                context.current_value
            )

            allocation = float(
                context.allocation_percent
            )

            portfolio_value = 0.0

            if allocation > 0:
                portfolio_value = (
                    current_value
                    / (allocation / 100)
                )

            if portfolio_value > 0:

                instrument_gap_amount = int(
                    portfolio_value
                    * allocation_gap_percent
                    / 100
                )

                theme_gap_amount = int(
                    portfolio_value
                    * theme_gap_percent
                    / 100
                )

                gap_amount = min(
                    instrument_gap_amount,
                    theme_gap_amount,
                )

            else:

                gap_amount = investable_cash

            if gap_amount <= 0:
                continue

            candidates.append(
                {
                    "market": market,
                    "recommendation": recommendation,
                    "price": price,
                    "current_allocation": current_allocation,
                    "allocation_gap_percent": (
                        allocation_gap_percent
                    ),
                    "current_theme_allocation": (
                        current_theme_allocation
                    ),
                    "theme_gap_percent": (
                        theme_gap_percent
                    ),
                    "gap_amount": gap_amount,
                    "score": recommendation.buy_score,
                    "primary_theme": primary_theme,
                }
            )

        if not candidates:
            return []

        # ---------------------------------------------------------------
        # Rank by conviction first.
        #
        # Theme gap is used as a secondary factor.
        # ---------------------------------------------------------------
        candidates.sort(
            key=lambda item: (
                item["score"],
                item["theme_gap_percent"],
                item["allocation_gap_percent"],
            ),
            reverse=True,
        )

        # ---------------------------------------------------------------
        # Only one instrument per primary theme.
        # ---------------------------------------------------------------
        candidates = cls._deduplicate_themes(
            candidates
        )

        if not candidates:
            return []

        selected = candidates[
            :max_positions
        ]

        total_score = sum(
            max(
                item["score"],
                1,
            )
            for item in selected
        )

        plans: list[InvestmentPlan] = []

        remaining_cash = investable_cash

        for item in selected:

            recommendation = (
                item["recommendation"]
            )

            price = item["price"]

            score_weight = (
                max(
                    recommendation.buy_score,
                    1,
                )
                / total_score
            )

            proposed_amount = int(
                investable_cash
                * score_weight
            )

            # Never exceed either:
            # 1. instrument allocation gap
            # 2. aggregate theme allocation gap
            proposed_amount = min(
                proposed_amount,
                item["gap_amount"],
                remaining_cash,
            )

            # Convert to executable whole shares.
            quantity = floor(
                proposed_amount
                / price
            )

            executable_amount = int(
                quantity * price
            )

            if (
                quantity <= 0
                or executable_amount <= 0
            ):
                continue

            remaining_cash -= (
                executable_amount
            )

            plans.append(
                InvestmentPlan(
                    symbol=item["market"].symbol,
                    amount=executable_amount,
                    score=recommendation.buy_score,
                    reason=", ".join(
                        recommendation.reasons[:3]
                    ),
                    quantity=quantity,
                    price=price,
                    target_allocation_percent=(
                        target_allocation_percent
                    ),
                    current_allocation_percent=(
                        item["current_allocation"]
                    ),
                    allocation_gap_amount=(
                        item["gap_amount"]
                    ),
                )
            )

            if remaining_cash <= 0:
                break

        return plans