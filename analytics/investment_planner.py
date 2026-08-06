from dataclasses import dataclass


@dataclass
class InvestmentPlan:

    symbol: str
    amount: int
    score: int
    reason: str
class InvestmentPlanner:

    @staticmethod
    def create_plan(
        recommendations,
        available_cash: int,
    ):
        """
        recommendations:
            List[RecommendationPair]
        """

        buy_list = [
            item
            for item in recommendations
            if item[1].action == "BUY"
        ]

        if not buy_list:
            return []

        buy_list.sort(
            key=lambda x: x[1].buy_score,
            reverse=True,
        )

        percentages = [
            0.40,
            0.30,
            0.20,
        ]

        plans = []

        for index, (market, recommendation) in enumerate(
            buy_list[:3]
        ):

            amount = int(
                available_cash
                * percentages[index]
            )

            plans.append(
                InvestmentPlan(
                    symbol=market.symbol,
                    amount=amount,
                    score=recommendation.buy_score,
                    reason=", ".join(
                        recommendation.reasons[:2]
                    ),
                )
            )

        return plans