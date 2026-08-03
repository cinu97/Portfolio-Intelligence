from __future__ import annotations

from market.models import AnalyticsResult
from market.models import MarketData


class AnalyticsService:

    @staticmethod
    def percentage(current: float, previous: float) -> float:

        if previous == 0:
            return 0.0

        return round(
            ((current - previous) / previous) * 100,
            2,
        )

    def calculate_score(
        self,
        day: float,
        t5: float,
        t7: float,
    ) -> tuple[int, str]:

        score = 50

        if t7 <= -5:
            score += 25

        if t5 <= -3:
            score += 20

        if day <= -1:
            score += 15

        if day > 0:
            score += 10

        score = min(score, 100)

        if score >= 85:
            recommendation = "⭐⭐⭐⭐⭐ Strong Buy"

        elif score >= 70:
            recommendation = "⭐⭐⭐⭐ Buy"

        elif score >= 55:
            recommendation = "⭐⭐⭐ Hold"

        elif score >= 40:
            recommendation = "⭐⭐ Watch"

        else:
            recommendation = "⭐ Wait"

        return score, recommendation

    def analyse(
        self,
        prices: list[MarketData],
    ) -> list[AnalyticsResult]:

        output = []

        for item in prices:

            t2 = self.percentage(
                item.live_price,
                item.t2_close,
            )

            t3 = self.percentage(
                item.live_price,
                item.t3_close,
            )

            t5 = self.percentage(
                item.live_price,
                item.t5_close,
            )

            t7 = self.percentage(
                item.live_price,
                item.t7_close,
            )

            score, recommendation = self.calculate_score(
                item.day_change_percent,
                t5,
                t7,
            )

            output.append(

                AnalyticsResult(

                    symbol=item.symbol,

                    live_price=item.live_price,

                    previous_close=item.previous_close,

                    day_change_percent=item.day_change_percent,

                    t2_percent=t2,

                    t3_percent=t3,

                    t5_percent=t5,

                    t7_percent=t7,

                    buy_score=score,

                    recommendation=recommendation,

                )

            )

        output.sort(
            key=lambda x: x.buy_score,
            reverse=True,
        )

        return output