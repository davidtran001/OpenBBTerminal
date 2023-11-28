"""FMP Literal Definitions."""

from typing import Literal

SECTORS = Literal[
    "Consumer Cyclical",
    "Energy",
    "Technology",
    "Industrials",
    "Financial Services",
    "Basic Materials",
    "Communication Services",
    "Consumer Defensive",
    "Healthcare",
    "Real Estate",
    "Utilities",
    "Industrial Goods",
    "Financial",
    "Services",
    "Conglomerates",
]

EXCHANGES = Literal[
    "amex",
    "ase",
    "asx",
    "ath",
    "bme",
    "bru",
    "bud",
    "bue",
    "cai",
    "cnq",
    "cph",
    "dfm",
    "doh",
    "etf",
    "euronext",
    "hel",
    "hkse",
    "ice",
    "iob",
    "ist",
    "jkt",
    "jnb",
    "jpx",
    "kls",
    "koe",
    "ksc",
    "kuw",
    "lse",
    "mex",
    "nasdaq",
    "neo",
    "nse",
    "nyse",
    "nze",
    "osl",
    "otc",
    "pnk",
    "pra",
    "ris",
    "sao",
    "sau",
    "set",
    "sgo",
    "shh",
    "shz",
    "six",
    "sto",
    "tai",
    "tlv",
    "tsx",
    "two",
    "vie",
    "wse",
    "xetra",
]

MARKETS = Literal[
    "AMEX",
    "AMS",
    "ASE",
    "ASX",
    "ATH",
    "BME",
    "BRU",
    "BUD",
    "BUE",
    "CAI",
    "CNQ",
    "CPH",
    "DFM",
    "DOH",
    "DUS",
    "ETF",
    "EURONEXT",
    "HEL",
    "HKSE",
    "ICE",
    "IOB",
    "IST",
    "JKT",
    "JNB",
    "JPX",
    "KLS",
    "KOE",
    "KSC",
    "KUW",
    "LSE",
    "MEX",
    "MIL",
    "NASDAQ",
    "NEO",
    "NSE",
    "NYSE",
    "NZE",
    "OSL",
    "OTC",
    "PNK",
    "PRA",
    "RIS",
    "SAO",
    "SAU",
    "SES",
    "SET",
    "SGO",
    "SHH",
    "SHZ",
    "SIX",
    "STO",
    "TAI",
    "TLV",
    "TSX",
    "TWO",
    "VIE",
    "WSE",
    "XETRA",
]

TRANSACTION_TYPES = Literal[
    "A-Award",
    "C-Conversion",
    "D-Return",
    "E-ExpireShort",
    "F-InKind",
    "G-Gift",
    "H-ExpireLong",
    "I-Discretionary",
    "J-Other",
    "L-Small",
    "M-Exempt",
    "O-OutOfTheMoney",
    "P-Purchase",
    "S-Sale",
    "U-Tender",
    "W-Will",
    "X-InTheMoney",
    "Z-Trust",
]
