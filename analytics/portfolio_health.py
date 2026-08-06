from dataclasses import dataclass


@dataclass
class PortfolioHealth:
    health_score: int
    diversification_score: int
    risk_score: int
    cash_score: int
    total_holdings: int
    top_opportunity: str
    weakest_position: str

class PortfolioHealthEngine:

    @staticmethod
    def calculate(results):
        """
        results = List[PortfolioResult]
        """

        total_holdings = len(results)

        buy_candidates = [
            r for r in results
            if r.recommendation.action == "BUY"
        ]

        top = max(
            results,
            key=lambda r: r.recommendation.score
        )

        weak = min(
            results,
            key=lambda r: r.recommendation.score
        )

        health_score = min(
            100,
            int(
                sum(r.recommendation.score for r in results)
                / total_holdings
            )
        )

        diversification = min(
            100,
            total_holdings * 4
        )

        risk = max(
            0,
            100 - len(buy_candidates) * 5
        )

        cash = 100

        return PortfolioHealth(
            health_score=health_score,
            diversification_score=diversification,
            risk_score=risk,
            cash_score=cash,
            total_holdings=total_holdings,
            top_opportunity=top.market.symbol,
            weakest_position=weak.market.symbol,
        )