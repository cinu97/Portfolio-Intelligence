from __future__ import annotations


ETF_THEMES: dict[str, tuple[str, ...]] = {
    # Broad market
    "NIFTYBEES": ("india_equity", "nifty"),
    "NIFTYETF": ("india_equity", "nifty"),
    "SENSEXETF": ("india_equity", "sensex"),
    "JUNIORBEES": ("india_equity", "nifty_next_50"),
    "HDFCNEXT50": ("india_equity", "nifty_next_50"),
    "SMALLCAP": ("india_equity", "small_cap"),
    "HDFCSML250": ("india_equity", "small_cap"),
    "MID150BEES": ("india_equity", "mid_cap"),

    # Banking / financials
    "BANKBEES": ("banking", "india_equity"),
    "BANKIETF": ("banking", "india_equity"),
    "SBIN": ("banking", "india_equity"),
    "BSE": ("financial_market", "india_equity"),

    # IT
    "ITETF": ("it_services", "technology"),
    "INTERNET": ("technology", "internet"),
    "WIPRO": ("it_services", "technology"),

    # Healthcare / pharma
    "PHARMABEES": ("pharma", "healthcare"),
    "HEALTHIETF": ("healthcare", "pharma"),

    # FMCG
    "FMCGIETF": ("fmcg", "consumer"),
    
    # Defence
    "MODEFENCE": ("defence", "industrial"),

    # Metals
    "METALIETF": ("metals", "commodities"),
    "MCX": ("commodities", "financial_market"),

    # Energy
    "OILIETF": ("oil", "energy"),

    # Precious metals
    "GOLDBEES": ("gold", "precious_metals"),
    "GOLDIETF": ("gold", "precious_metals"),
    "GOLDCASE": ("gold", "precious_metals"),
    "SETFGOLD": ("gold", "precious_metals"),

    "SILVERIETF": ("silver", "precious_metals"),

    # REITs
    "MINDSPACE-RR": ("reit", "real_estate"),
    "EMBASSY-RR": ("reit", "real_estate"),
    "BIRET-RR": ("reit", "real_estate"),
    "NXST-RR": ("reit", "real_estate"),
    "MOREALTY": ("real_estate", "reit"),

    # Government / PSU
    "CPSEETF": ("psu", "india_equity"),

    # Dividend
    "DIVOPPBEES": ("dividend", "india_equity"),

    # Cash / liquid
    "LIQUIDBEES": ("cash", "liquid"),
    "LIQUIDCASE": ("cash", "liquid"),

    # Banking / financial
    "FINIETF": ("financials", "india_equity"),
    "EBBETF0430": ("financials", "india_equity"),
    "NV20BEES": ("value", "india_equity"),
    "AUTOIETF": ("automobile", "india_equity"),
}


def themes_for_symbol(symbol: str) -> tuple[str, ...]:
    """Return configured themes for an instrument."""
    return ETF_THEMES.get(
        symbol.upper(),
        ("india_equity",),
    )