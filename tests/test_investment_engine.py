from __future__ import annotations

import unittest

import pandas as pd

from analytics.intelligence.intelligence import NewsIntelligence
from analytics.intelligence.models import NewsItem, SignalDirection
from market.inav import INAVService
from market.inav_mapping import ETF_INAV_MAP
from market.technicals import TechnicalService
from portfolio.loader import PortfolioLoader
from analytics.intelligence.themes import metadata_for_symbol, list_known_symbols, themes_for_symbol


class InstrumentMetadataTests(unittest.TestCase):
    def test_all_current_holdings_have_explicit_metadata(self):
        symbols = PortfolioLoader().get_symbols()
        self.assertGreater(len(symbols), 40)
        missing = []
        for symbol in symbols:
            meta = metadata_for_symbol(symbol)
            if meta is None:
                missing.append(symbol)
            elif not meta.symbol:
                missing.append(symbol)
        self.assertEqual(missing, [], msg=f"Missing metadata: {missing}")

    def test_known_symbols_have_explicit_non_generic_theme_metadata(self):
        for symbol in ["INDNIPPON", "IVZBANKNF", "IVZSENSEX", "MON100"]:
            meta = metadata_for_symbol(symbol)
            self.assertIsNotNone(meta)
            self.assertNotEqual(meta.primary_theme, "unknown")
            self.assertNotIn("india_equity", meta.themes)


class INAVProviderTests(unittest.TestCase):
    def test_provider_routing_is_explicit_for_key_etfs(self):
        expected = {
            "AUTOIETF": "invesco",
            "LIQUIDCASE": "mirae",
            "FINIETF": "nippon",
            "METALIETF": "mirae",
            "HEALTHIETF": "mirae",
            "SILVERIETF": "mirae",
            "EBBETF0430": "mirae",
            "INDNIPPON": "nippon",
            "IVZBANKNF": "invesco",
            "IVZSENSEX": "invesco",
            "MON100": "yahoo",
        }
        for symbol, provider in expected.items():
            self.assertEqual(INAVService.provider_for_symbol(symbol), provider)

    def test_provider_mapping_has_verified_records(self):
        for symbol in ["AUTOIETF", "LIQUIDCASE", "FINIETF", "METALIETF", "HEALTHIETF", "SILVERIETF", "EBBETF0430", "INDNIPPON", "IVZBANKNF", "IVZSENSEX", "MON100"]:
            self.assertIn(symbol, ETF_INAV_MAP or set())


class TechnicalIndicatorTests(unittest.TestCase):
    def test_rsi_14_and_ema_63_are_calculated(self):
        df = pd.DataFrame({
            "Close": [100, 101, 102, 103, 101, 104, 108, 110, 112, 109, 111, 113, 116, 118, 120, 121, 122, 124, 123, 126]
        })
        metrics = TechnicalService.calculate(df)
        self.assertIn("rsi14", metrics)
        self.assertIn("ema63", metrics)
        self.assertGreaterEqual(metrics["rsi14"], 0)
        self.assertLessEqual(metrics["rsi14"], 100)
        self.assertGreater(metrics["ema63"], 0)


class NewsIntelligenceTests(unittest.TestCase):
    def test_news_intelligence_uses_symbol_metadata_and_is_numeric(self):
        class DummyProvider:
            def fetch(self, limit_per_feed=20):
                return [
                    NewsItem(title="SBI boosts credit growth outlook", source="times-now", url="https://example.com/1", published_at=None, summary="Banking credit growth rises as RBI supports loan expansion.", themes=("banking",)),
                    NewsItem(title="Fed signals rates stay higher for longer", source="reuters", url="https://example.com/2", published_at=None, summary="US rates and technology volatility continue.", themes=("technology",)),
                ]

        intelligence = NewsIntelligence(provider=DummyProvider())
        signal = intelligence.evaluate("SBIN")
        self.assertIn(signal.direction, (SignalDirection.BULLISH, SignalDirection.NEUTRAL, SignalDirection.BEARISH))
        self.assertGreaterEqual(signal.score, -10)
        self.assertLessEqual(signal.score, 10)
        self.assertTrue(signal.reasons)


if __name__ == "__main__":
    unittest.main()
