from __future__ import annotations

# Explicit ETF -> iNAV provider route and NSE key mapping.
# This avoids inferring routing from ticker naming.

ETF_INAV_MAP: dict[str, str] = {
    "NIFTYBEES": "NIFTYBEINAV",
    "BANKBEES": "BANKBEINAV",
    "GOLDBEES": "GOLDBEINAV",
    "SILVERBEES": "SILVERBEINAV",
    "PHARMABEES": "PHARMABEINAV",
    "ITBEES": "ITBEINAV",
    "AUTOIETF": "AUTOIETFINAV",
    "CPSEETF": "CPSEETFINAV",
    "GOLDIETF": "GOLDIETFINAV",
    "LIQUIDCASE": "LIQUIDCASEINAV",
    "FINIETF": "FINIETFINAV",
    "METALIETF": "METALIETFINAV",
    "HEALTHIETF": "HEALTHIETFINAV",
    "SILVERIETF": "SILVERIETFINAV",
    "EBBETF0430": "EBBETF0430NAV",
    "INDNIPPON": "INDNIPPONNAV",
    "IVZBANKNF": "IVZBANKNFNAV",
    "IVZSENSEX": "IVZSENSEXNAV",
    "MON100": "MON100NAV",
}

INAV_PROVIDER_ROUTING: dict[str, str] = {
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

SUPPORTED_INAV_SYMBOLS = frozenset(ETF_INAV_MAP)