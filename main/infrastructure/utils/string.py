class StringUtil:
    @staticmethod
    def number2srt(number) -> str:
        flag = ''
        if number < 0:
            flag = '-'

        number = round(float(number), 2)
        number = abs(number)
        if number < 10000:
            return flag + str(round(number / 1000, 2)) + "千"
        if 10000 < number < 100000000:
            return flag + str(round(number / 10000, 2)) + "万"

        return flag + str(round((number / 100000000), 2)) + "亿"
