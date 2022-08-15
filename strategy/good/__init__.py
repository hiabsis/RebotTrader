import math


def f_dyn(para, adapt_pct, min_length, max_length):
    dyna_len = 0
    i_len = (min_length + max_length) / 2
    if para:
        i_len = math.max(min_length, i_len * adapt_pct)
    else:
        i_len = math.min(min_length, i_len * (2 - adapt_pct))

    pass


def f_boolean(chka, reference_a):
    result_bool = False
    for item in chka:
        if item is True:
            result_bool = item
            break
    for index in range(0, len(chka)):
        if chka[item]:
            result_bool = reference_a[item] and result_bool

    return result_bool

#
# def f_relative_strength(t, vol_src, vol_len, _open, _high, _low, _close):
#     result = 0
#     if t == 'TFS Volume Oscillator':
#         iff_1    = close < _open ? -vol_src : 0
#         naccvol  = math.sum(_close > _open ? vol_src : iff_1, vol_len)
#         result  := naccvol / vol_len
#         result
#     if t == 'On Balance Volume':
#         result  := ta.cum(math.sign(ta.change(_close)) * vol_src)
#         result
#     if t == 'Klinger Volume Oscillator':
#         fastx    = I_volfastlen
#         slowx    = I_volslowlen
#         xtrend   = _close > _close[1] ? vol * 100 : -vol * 100
#         xfast    = ta.ema(xtrend, fastx)
#         xslow    = ta.ema(xtrend, slowx)
#         result  := xfast - xslow
#         result
#     if t == 'Cumulative Volume Oscillator':
#         result  := f_volcalc(vol_src, _open, _high, _low, _close)
#         result
#     if t == 'Volume Zone Oscillator':
#         result  := f_volzosc(vol_src, _close)
#         result
#     result


# tk_volume = True,
# tk_volatility = True
# tk_chikou_trend_filter = True
#
# tk_signal =
#
# tk_br_vo_lup = tk_signal > i_vol_peak
# tkarray = [tk_volume, tk_volatility, tk_chikou_trend_filter]
# tkvolarray = [1, 2, 3]
# booltkup = f_boolean(tkarray, tkvolarray)
#
# dyntk = f_dyn(booltkup, i_tk_dyn_perc, i_tk_min_len, i_tk_max_len)
#
# altsrcres =