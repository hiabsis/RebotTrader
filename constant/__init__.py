k_lines_csv_head = ["Time", "Open", "Close", "High", "Low", "Volume"]
# 不同时间级别所对应的corn表达式
interval_corn = {
    "1m": "0 0/1 * * * ?",
    "5m": "0 0/5 * * * ?",
    "15m": "0 0/15 * * * ? ",
    "30m": "0 0/30 * * * ?",
    "1h": "* * 0/1 * * ? ",
    "2h": "* * 0/2 * * ? ",
    "4h": "* * 0/4 * * ? ",
    "1d": "* * * 1/1 * ? *",
}
# 不同时间级别对应的秒数
interval_second = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "30m": 1800,
    "1h": 3600,
    "2h": 72000,
    "4h": 14400,
    "1d": 86400,
}
# 币安的虚拟货币类型

coin_symbol = [
    "1INCH",
    "AAVE",
    "ACA",
    "ACH",
    "ADA",
    "AGLD",
    "AION",
    "AKRO",
    "ALCX",
    "ALGO",
    "ALICE",
    "ALPACA",
    "ALPHA",
    "AMP",
    "ANC",
    "ANKR",
    "ANT",
    "ANY",
    "APE",
    "API3",
    "ARDR",
    "ARPA",
    "AR",
    "ASTR",
    "ATA",
    "ATOM",
    "AUDIO",
    "AUD",
    "AUTO",
    "AVAX",
    "AXS",
    "BADGER",
    "BAKE",
    "BAL",
    "BAND",
    "BAT",
    "BCH",
    "BEAM",
    "BEL",
    "BETA",
    "BICO",
    "BLZ",
    "BNB",
    "BNT",
    "BNX",
    "BOND",
    "BSW",
    "BTCST",
    "BTC",
    "BTG",
    "BTS",
    "BTTC",
    "BTT",
    "BURGER",
    "BUSD",
    "BZRX",
    "C98",
    "CAKE",
    "CELO",
    "CELR",
    "CFX",
    "CHESS",
    "CHR",
    "CHZ",
    "CKB",
    "CLV",
    "COCOS",
    "COMP",
    "COS",
    "COTI",
    "CRV",
    "CTK",
    "CTSI",
    "CTXC",
    "CVC",
    "CVP",
    "CVX",
    "DAR",
    "DASH",
    "DATA",
    "DCR",
    "DEGO",
    "DENT",
    "DEXE",
    "DGB",
    "DIA",
    "DNT",
    "DOCK",
    "DODO",
    "DOGE",
    "DOT",
    "DREP",
    "DUSK",
    "DYDX",
    "EGLD",
    "ELF",
    "ENJ",
    "ENS",
    "EOS",
    "EPS",
    "EPX",
    "ERN",
    "ETC",
    "ETH",
    "EUR",
    "FARM",
    "FET",
    "FIDA",
    "FIL",
    "FIO",
    "FIRO",
    "FIS",
    "FLM",
    "FLOW",
    "FLUX",
    "FORTH",
    "FOR",
    "FTM",
    "FTT",
    "FUN",
    "FXS",
    "GALA",
    "GAL",
    "GBP",
    "GLMR",
    "GMT",
    "GNO",
    "GRT",
    "GTC",
    "GTO",
    "GXS",
    "HARD",
    "HBAR",
    "HIGH",
    "HIVE",
    "HNT",
    "HOT",
    "ICP",
    "ICX",
    "IDEX",
    "ILV",
    "IMX",
    "INJ",
    "IOST",
    "IOTA",
    "IOTX",
    "IRIS",
    "JASMY",
    "JOE",
    "JST",
    "KAVA",
    "KDA",
    "KEEP",
    "KEY",
    "KLAY",
    "KMD",
    "KNC",
    "KP3R",
    "KSM",
    "LDO",
    "LEND",
    "LEVER",
    "LINA",
    "LINK",
    "LIT",
    "LOKA",
    "LPT",
    "LRC",
    "LSK",
    "LTC",
    "LTO",
    "LUNA",
    "MANA",
    "MASK",
    "MATIC",
    "MBL",
    "MBOX",
    "MC",
    "MDT",
    "MDX",
    "MFT",
    "MINA",
    "MIR",
    "MITH",
    "MKR",
    "MLN",
    "MOB",
    "MOVR",
    "MTL",
    "NANO",
    "NBS",
    "NEAR",
    "NEO",
    "NEXO",
    "NKN",
    "NMR",
    "NPXS",
    "NULS",
    "NU",
    "OCEAN",
    "OGN",
    "OG",
    "OMG",
    "OM",
    "ONE",
    "ONG",
    "ONT",
    "OOKI",
    "OP",
    "ORN",
    "OXT",
    "PAXG",
    "PEOPLE",
    "PERL",
    "PERP",
    "PHA",
    "PLA",
    "PNT",
    "POLS",
    "POLY",
    "POND",
    "POWR",
    "PUNDIX",
    "PYR",
    "QI",
    "QNT",
    "QTUM",
    "QUICK",
    "RAD",
    "RAMP",
    "RARE",
    "RAY",
    "REEF",
    "REI",
    "REN",
    "REP",
    "REQ",
    "RGT",
    "RLC",
    "RNDR",
    "ROSE",
    "RSR",
    "RUNE",
    "RVN",
    "SAND",
    "SCRT",
    "SC",
    "SFP",
    "SHIB",
    "SKL",
    "SLP",
    "SNX",
    "SOL",
    "SPELL",
    "SRM",
    "STMX",
    "STORJ",
    "STPT",
    "STRAX",
    "STX",
    "SUN",
    "SUPER",
    "SUSHI",
    "SXP",
    "SYS",
    "TCT",
    "TFUEL",
    "THETA",
    "TKO",
    "TLM",
    "TOMO",
    "TORN",
    "TRB",
    "TRIBE",
    "TROY",
    "TRU",
    "TRX",
    "T",
    "TUSD",
    "TVK",
    "TWT",
    "UMA",
    "UNFI",
    "UNI",
    "USDC",
    "UST",
    "UTK",
    "VET",
    "VGX",
    "VIDT",
    "VITE",
    "VOXEL",
    "VTHO",
    "WAN",
    "WAVES",
    "WAXP",
    "WING",
    "WIN",
    "WNXM",
    "WOO",
    "WRX",
    "WTC",
    "XEC",
    "XEM",
    "XLM",
    "XMR",
    "XRP",
    "XTZ",
    "XVS",
    "XZC",
    "YFII",
    "YFI",
    "YGG",
    "ZEC",
    "ZEN",
    "ZIL",
    "ZRX"
]
