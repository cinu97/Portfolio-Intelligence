from analytics.rules.average_buy import AverageBuyRule
from analytics.rules.allocation import AllocationRule
from analytics.rules.momentum import MomentumRule
from analytics.rules.fifty_two_week import FiftyTwoWeekRule
from analytics.rules.moving_average import MovingAverageRule
from analytics.portfolio_context import PortfolioContext


class ScoringEngine:

    @staticmethod
    def calculate(portfolio: PortfolioContext) -> tuple[int, list[str]]:

        score = 0

        reasons = []

        avg = AverageBuyRule.calculate(
            portfolio.average_price,
            portfolio.current_price,
        )

        allocation = AllocationRule.calculate(
            portfolio.allocation_percent,
        )

        momentum = MomentumRule.calculate(
            portfolio.day_percent,
            portfolio.t5_percent,
            portfolio.t7_percent,
        )

        week52 = FiftyTwoWeekRule.calculate(
            portfolio.range_percent,
        )

        dma = MovingAverageRule.calculate(
            portfolio.current_price,
            portfolio.dma50,
            portfolio.dma200,
        )

        score += avg.score
        score += allocation.score
        score += momentum.score
        score += week52.score
        score += dma.score

        reasons.append(avg.reason)
        reasons.append(allocation.reason)

        reasons.extend(momentum.reasons)
        reasons.extend(week52.reasons)
        reasons.extend(dma.reasons)

        return min(score, 100), reasons
