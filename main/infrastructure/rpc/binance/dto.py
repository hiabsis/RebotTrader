from main.infrastructure.utils.json import JsonUtil
from main.infrastructure.utils.date import DateUtil


class KLineDTO:

    def __init__(self, *args, **kwargs):
        self.open_time = None
        self.open_price = None
        self.close_price = None
        self.high_price = None
        self.low_price = None
        self.volume = None
        # 交易数量
        self.trade_number = None
        self.asset = None
        self.symbol = ""
        self.interval = ""
        super(KLineDTO, self).__init__(*args, **kwargs)

    def build(self, k_line: list, symbol, interval):
        self.open_time = DateUtil.timestamp2str(int(k_line[0]) / 1000)
        self.open_price = round(float(k_line[1]), 6)
        self.high_price = round(float(k_line[2]), 6)
        self.low_price = round(float(k_line[3]), 6)
        self.close_price = round(float(k_line[4]), 6)
        self.volume = round(float(k_line[5]), 6)
        self.asset = round(float(k_line[7]), 6)
        self.trade_number = round(float(k_line[8]), 6)
        self.symbol = symbol
        self.interval = interval


class QueryKLinesDTO:

    def __init__(self):
        self.data: list[KLineDTO] = []
        self.is_success = True

    def to_dict(self):
        return JsonUtil.object2json(self)
