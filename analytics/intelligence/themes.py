from __future__ import annotations

from analytics.intelligence.models import InstrumentMetadata

ETF_THEMES: dict[str, tuple[str, ...]] = {
    "NIFTYBEES": ("india_equity", "nifty", "equity_index"),
    "NIFTYETF": ("india_equity", "nifty", "equity_index"),
    "SENSEXETF": ("india_equity", "sensex", "equity_index"),
    "JUNIORBEES": ("india_equity", "nifty_next_50", "equity_index"),
    "HDFCNEXT50": ("india_equity", "nifty_next_50", "equity_index"),
    "SMALLCAP": ("india_equity", "small_cap", "equity_index"),
    "HDFCSML250": ("india_equity", "small_cap", "equity_index"),
    "MID150BEES": ("india_equity", "mid_cap", "equity_index"),
    "BANKBEES": ("banking", "financials", "india_equity"),
    "BANKIETF": ("banking", "financials", "india_equity"),
    "SBIN": ("banking", "financials", "india_equity"),
    "BSE": ("financial_market", "financials", "india_equity"),
    "GAIL": ("energy", "oil_gas", "india_equity"),
    "ITETF": ("it_services", "technology", "india_equity"),
    "INTERNET": ("technology", "internet", "india_equity"),
    "INFRABEES": ("infrastructure", "capital_goods", "india_equity"),
    "WIPRO": ("it_services", "technology", "india_equity"),
    "PHARMABEES": ("pharma", "healthcare", "india_equity"),
    "HEALTHIETF": ("healthcare", "pharma", "india_equity"),
    "FMCGIETF": ("fmcg", "consumer", "india_equity"),
    "MODEFENCE": ("defence", "industrial", "india_equity"),
    "METALIETF": ("metals", "commodities", "india_equity"),
    "MCX": ("commodities", "financial_market", "india_equity"),
    "OILIETF": ("oil", "energy", "india_equity"),
    "ENERGY": ("energy", "oil", "india_equity"),
    "LALITHAA": ("consumer", "retail", "india_equity"),
    "MAFANG": ("technology", "internet", "china_equity"),
    "MAHKTECH": ("technology", "it_services", "india_equity"),
    "MASPTOP50": ("equity_index", "nifty", "india_equity"),
    "PSUBANK": ("banking", "financials", "india_equity"),
    "GOLDBEES": ("gold", "precious_metals", "commodities"),
    "GOLDIETF": ("gold", "precious_metals", "commodities"),
    "GOLDCASE": ("gold", "precious_metals", "commodities"),
    "SETFGOLD": ("gold", "precious_metals", "commodities"),
    "SILVERIETF": ("silver", "precious_metals", "commodities"),
    "MINDSPACE-RR": ("reit", "real_estate", "india_equity"),
    "EMBASSY-RR": ("reit", "real_estate", "india_equity"),
    "BIRET-RR": ("reit", "real_estate", "india_equity"),
    "NXST-RR": ("reit", "real_estate", "india_equity"),
    "MOREALTY": ("real_estate", "reit", "india_equity"),
    "CPSEETF": ("psu", "india_equity", "financials"),
    "DIVOPPBEES": ("dividend", "india_equity", "equity_index"),
    "LIQUIDBEES": ("cash", "liquid", "fixed_income"),
    "LIQUIDCASE": ("cash", "liquid", "fixed_income"),
    "FINIETF": ("financials", "india_equity", "banking"),
    "EBBETF0430": ("financials", "india_equity", "banking"),
    "NV20BEES": ("value", "india_equity", "equity_index"),
    "NIFTYADD": ("equity_index", "nifty", "india_equity"),
    "AUTOIETF": ("automobile", "india_equity", "consumer"),
    "INDNIPPON": ("equity_index", "nifty"),
    "IVZBANKNF": ("banking", "financials"),
    "IVZSENSEX": ("equity_index", "sensex"),
    "MON100": ("technology", "us_equity", "nasdaq_100"),
}

DEFAULT_METADATA: dict[str, InstrumentMetadata] = {
    "INDNIPPON": InstrumentMetadata(
        symbol="INDNIPPON",
        yahoo_symbol="INDNIPPON.NS",
        instrument_type="ETF",
        provider="Nippon",
        underlying_index="Nifty 50",
        primary_theme="equity_index",
        themes=("equity_index", "nifty"),
        asset_class="equity",
        inav_provider="nippon",
        news_search_terms=("Nifty 50", "India equity", "Indian market"),
        news_themes=("equity_index", "macro"),
        geographic_exposure="India",
    ),
    "IVZBANKNF": InstrumentMetadata(
        symbol="IVZBANKNF",
        yahoo_symbol="IVZBANKNF.NS",
        instrument_type="ETF",
        provider="Invesco",
        underlying_index="Nifty Bank",
        primary_theme="banking",
        themes=("banking", "financials"),
        asset_class="equity",
        inav_provider="invesco",
        news_search_terms=("Nifty Bank", "banking sector", "Indian banks"),
        news_themes=("banking", "financials", "macro"),
        geographic_exposure="India",
    ),
    "IVZSENSEX": InstrumentMetadata(
        symbol="IVZSENSEX",
        yahoo_symbol="IVZSENSEX.NS",
        instrument_type="ETF",
        provider="Invesco",
        underlying_index="Sensex",
        primary_theme="equity_index",
        themes=("equity_index", "sensex"),
        asset_class="equity",
        inav_provider="invesco",
        news_search_terms=("Sensex", "Indian equities", "BSE market"),
        news_themes=("equity_index", "macro"),
        geographic_exposure="India",
    ),
    "MON100": InstrumentMetadata(
        symbol="MON100",
        yahoo_symbol="^NDX",
        instrument_type="ETF",
        provider="NSE/Index",
        underlying_index="NASDAQ-100",
        primary_theme="technology",
        themes=("technology", "us_equity", "nasdaq_100"),
        asset_class="equity",
        inav_provider="yahoo",
        news_search_terms=("NASDAQ-100", "US technology", "Fed rates"),
        news_themes=("technology", "us_macro", "macro"),
        geographic_exposure="United States",
    ),
}


def symbols_with_metadata() -> list[str]:
    return sorted(set(ETF_THEMES) | set(DEFAULT_METADATA))


def metadata_for_symbol(symbol: str) -> InstrumentMetadata | None:
    normalized = symbol.strip().upper()
    if normalized in DEFAULT_METADATA:
        return DEFAULT_METADATA[normalized]
    if normalized not in ETF_THEMES:
        return None
    themes = ETF_THEMES[normalized]
    primary_theme = next((theme for theme in themes if theme not in {"india_equity"}), themes[0] if themes else "unknown")
    return InstrumentMetadata(
        symbol=normalized,
        yahoo_symbol=f"{normalized}.NS",
        instrument_type="ETF",
        provider="",
        underlying_index="",
        primary_theme=primary_theme,
        themes=themes,
        asset_class="equity",
        inav_provider="",
        news_search_terms=(normalized, *themes),
        news_themes=themes,
        geographic_exposure="India",
    )


def themes_for_symbol(symbol: str) -> tuple[str, ...]:
    metadata = metadata_for_symbol(symbol)
    if metadata is None:
        return ("unknown",)
    return metadata.themes


def list_known_symbols() -> list[str]:
    return symbols_with_metadata()


def validate_symbol_metadata(symbols: list[str]) -> list[str]:
    missing: list[str] = []
    for symbol in symbols:
        meta = metadata_for_symbol(symbol)
        if meta is None or not meta.symbol or meta.primary_theme == "unknown":
            missing.append(symbol)
    return missing