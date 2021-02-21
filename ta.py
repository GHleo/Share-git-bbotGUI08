import math
import numpy as np
import configGlb as cnf
import statistics as sts
from datetime import datetime
# Считается, что, на коротких отрезках лучше использовать экспоненциальное среднее скользящее, а на длинных — простое.
# Simple moving average
# https://en.wikipedia.org/wiki/Moving_average
def SMA(data, period):
    if len(data) == 0:
        raise Exception("Empty data")
    if period <= 0:
        raise Exception("Invalid period")

    interm = 0
    result = []
    nan_inp = 0

    for i, v in enumerate(data):
        if math.isnan(data[i]):
            result.append(math.nan)
            interm = 0
            nan_inp += 1
        else:
            interm += v
            if (i + 1 - nan_inp) < period:
                result.append(math.nan)
            else:
                result.append(interm / float(period))
                if not math.isnan(data[i + 1 - period]):
                    interm -= data[i + 1 - period]
    return result


# Calculates various EMA with different smoothing multipliers, see lower
def generalEMA(data, period, multiplier):
    if period <= 1:
        raise Exception("Invalid period")

    sma = SMA(data, period)

    result = []
    for k, v in enumerate(sma):
        if math.isnan(v):
            result.append(math.nan)
        else:
            prev = result[k - 1]
            if math.isnan(prev):
                result.append(v)
                continue
            ema = (data[k] - prev) * multiplier + prev
            result.append(ema)
    return result


# Exponential moving average
# https://en.wikipedia.org/wiki/Moving_average#Exponential_moving_average
def EMA(data, period):
    return generalEMA(data, period, 2 / (float(period) + 1.0))


# Synonym to EMA
def EWMA(data, period):
    return EMA(data, period)


# Modified moving average
# https://en.wikipedia.org/wiki/Moving_average
def SMMA(data, period):
    return generalEMA(data, period, 1 / (float(period)))


# Synonym to SMMA
def RMA(data, period):
    return SMMA(data, period)


# Synonym to SMMA
def MMA(data, period):
    return SMMA(data, period)


# Double exponential moving average
# https://en.wikipedia.org/wiki/Double_exponential_moving_average
def D2(data, period):
    ema = EMA(data, period)
    ema_ema = EMA(ema, period)
    e2 = list(map(lambda x: x * 2, ema))

    result = []

    for i in range(len(data)):
        result.append(e2[i] - ema_ema[i])
    return result


# Double exponential moving average
def DEMA(data, period):
    return D2(data, period)


# Double exponential moving average
def DMA(data, period):
    return D2(data, period)


# Triple Exponential Moving Average
# https://en.wikipedia.org/wiki/Triple_exponential_moving_average
def T3(data, period):
    e1 = EMA(data, period)
    e2 = EMA(e1, period)
    e3 = EMA(e2, period)

    e1 = list(map(lambda x: x * 3, e1))
    e2 = list(map(lambda x: x * 3, e2))

    result = []
    for i in range(len(data)):
        result.append(e1[i] - e2[i] + e3[i])

    return result


# Triple Exponential Moving Average
def TEMA(data, period):
    return T3(data, period)


# Triple Exponential Moving Average
def TMA(data, period):
    return T3(data, period)


# Moving average convergence/divergence
# https://en.wikipedia.org/wiki/MACD
def MACD(data, fastperiod, slowperiod, signalperiod):
    # closes = [float(x[4]) for x in data]
    # closes_time = [float(x[6]) for x in data]
    # dt_ =  [datetime.fromtimestamp(x / 1000.0) for x in closes_time]
    #print('!!!! from ta.py closes->', closes)
    #print('!!!! from ta.py closes time->', dt_)
    macd, macdsignal, macdhist = [], [], []

    fast_ema = EMA(data, fastperiod)
    slow_ema = EMA(data, slowperiod)
    # print('count in closes (from MACD) - ',len(data))
    # print('count in fast_ema (from MACD) - ',len(fast_ema))
    # print('count in slow_ema (from MACD) - ',len(slow_ema))
    # fast_ema = EMA(closes, fastperiod)
    # slow_ema = EMA(closes, slowperiod)
    indexPosList = []

    diff = []

    for k, fast in enumerate(fast_ema):
        if math.isnan(fast) or math.isnan(slow_ema[k]):
            macd.append(math.nan)
            macdsignal.append(math.nan)
        else:
            macd.append(fast - slow_ema[k])
            diff.append(macd[k])

    diff_ema = EMA(diff, signalperiod)
    macdsignal = macdsignal + diff_ema

    for k, ms in enumerate(macdsignal):
        if math.isnan(ms) or math.isnan(macd[k]):
            macdhist.append(math.nan)
        else:
            macdhist.append(macd[k] - macdsignal[k])

    return macd, macdsignal, macdhist


# Relative strength index
# https://en.wikipedia.org/wiki/Relative_strength_index
def RSI(data, period):
    u_days = []
    d_days = []

    for i, _ in enumerate(data):
        if i == 0:
            u_days.append(0)#first value data Set 0
            d_days.append(0)#first value data Set 0
        else:
            if data[i] > data[i - 1]:
                u_days.append(data[i] - data[i - 1])#Up periods are characterized by the close being higher than the previous close
                d_days.append(0)
            elif data[i] < data[i - 1]:
                d_days.append(data[i - 1] - data[i])#a down period is characterized by the close being lower than the previous period's close
                u_days.append(0)
            else:
                u_days.append(0)
                d_days.append(0)

    smma_u = SMMA(u_days, period)
    smma_d = SMMA(d_days, period)

    result = []

    for k, _ in enumerate(data):
        if smma_d[k] == 0:
            result.append(100)
        else:
            result.append(100 - (100 / (1 + smma_u[k] / smma_d[k])))

    return result


# Stochastic oscillator
# https://en.wikipedia.org/wiki/Stochastic_oscillator
def STOCH(high, low, closes, fastk_period, slowk_period, slowd_period):
    fastk = []

    for i, _ in enumerate(closes):
        if (i + 1) < fastk_period:
            fastk.append(math.nan)
        else:
            lower_bound = i + 1 - fastk_period
            upper_bound = i + 1
            curr_low = min(low[lower_bound:upper_bound])
            curr_high = max(high[lower_bound:upper_bound])
            fastk.append(((closes[i] - curr_low) / (curr_high - curr_low)) * 100)

    fastk = EMA(fastk, slowk_period)
    slowd = EMA(fastk, slowd_period)

    return fastk, slowd


# RSI + STOCH
# https://www.investopedia.com/terms/s/stochrsi.asp
def STOCHRSI(data, period, fastk_period, fastd_period):
    rsi = RSI(data, period)
    return STOCH(rsi, rsi, rsi, period, fastk_period, fastd_period)


# Bollinger Bands
# https://en.wikipedia.org/wiki/Bollinger_Bands
def BBANDS(data, ma=SMA, ma_period=20, dev_val=2):
    middle = ma(data, ma_period)

    # calculating stddev. We won't count NaN values. Also NaNs are reasons not to use statistics.stddev, numpy, etc.
    stddevs = []
    real_data_cnt = 0

    for i in range(len(data)):
        if math.isnan(middle[i]):
            stddevs.append(0)
            real_data_cnt += 1
            continue

        if i - real_data_cnt >= ma_period:
            avg = sum(middle[i - ma_period + 1:i + 1]) / ma_period
            s = sum(map(lambda x: math.pow(x - avg, 2), middle[i - ma_period + 1:i + 1]))
            stddev_avg = s / ma_period
            stddev = math.sqrt(stddev_avg)
            stddevs.append(stddev)
        else:
            stddevs.append(0)

    upper = []
    lower = []
    for i in range(len(middle)):
        if not math.isnan(middle[i]):
            upper.append(middle[i] + stddevs[i] * dev_val)
            lower.append(middle[i] - stddevs[i] * dev_val)
        else:
            upper.append(math.nan)
            lower.append(math.nan)
    return upper, middle, lower

#INDICATORS:
# WR (Williams %R) - is a momentum indicator, which gauges if a stock is overbought or oversold.  https://www.tradingview.com/wiki/Williams_%25R_(%25R)
def WR(Cl,H,L,prd):
    try:
        # print('H -> ',H)
        # print('H [-14:]  -> ',H[-prd:])#
        # print('H [-14]  -> ',H[-14])
        # print('max(H) -> ',max(H))
        Hprd = H[-prd:]
        Lprd = L[-prd:]
        Cl_last = Cl[-1]

        # print('Cl -> ', Cl)
        print('Cl [-prd:]  -> ', Cl[-prd:])
        # print('Cl[-1]  -> ',Cl[-1])
        wr = (max(Hprd) - Cl_last) / (max(Hprd) - min(Lprd)) * -100
        return wr
    except Exception as e:
        print('Exception from WR ', e)
# технический индикатор, определяющий состояние перекупленности/перепроданности по положению текущей цены закрытия в диапазоне между минимумом и максимумом цен за предыдущие периоды
def WR_Extremum(Cl,H,L,prd):
    try:
        UpExtr, DnExtr,w_prd = [],[],[]
        Hprd = H[-prd:]
        Lprd = L[-prd:]
        Clprd = Cl[-prd:]
        Cl_last = Cl[-1]
        h_dbl = H[-prd*2:] # expand list by 2 to left side
        l_dbl = L[-prd*2:] # expand list by 2 to left side

        for i,x in enumerate(Clprd):
            #print('i INDEX',i)
            #wr_= (max(h_dbl[i:prd+i]) - x) / (max(h_dbl[i:prd+i]) - min(l_dbl[i:prd+i])) * -100
            wr_ = (x - max(h_dbl[i:prd + i])) / (max(h_dbl[i:prd + i]) - min(l_dbl[i:prd + i])) * 100
            w_prd.append(wr_)

            if wr_ <= -60: DnExtr.append(wr_)
            if wr_ >= -20: UpExtr.append(wr_)

        #wr = (max(Hprd) - Cl_last) / (max(Hprd) - min(Lprd)) * -100
        wr_curr = (Cl_last-max(Hprd))  / (max(Hprd) - min(Lprd)) * 100
        return w_prd,UpExtr,DnExtr,wr_curr
    except Exception as e:
        print('Exception from WR_Extremum ', e)
#Momentum is the measurement of the speed or velocity of price changes.
def MTM(Close,cur_rate):
    try:
        Cl_last, Cl_first = cur_rate, Close[0]
        Cl_last3, Cl_last3_prd = Close[-3],Close[-3:] #last 3 candles
        Cl_last20, Cl_last20_prd = Close[-20], Close[-20:]
        mtmPrd, mtmLast20, mtmLast3 = [0,0],[0,0],[0,0]

        listInPrcnt = chngPercentList(Close)
        stdev = round(sts.stdev(listInPrcnt[1:]),2) #Volatility for period

        listInPrcnt10 = chngPercentList(Cl_last20_prd) #Volatility for last 10 candles
        stdev10 = round(sts.stdev(listInPrcnt10[1:]),2)
        #print('Extremums()... close last 10 Volatility-> ',stdev10)

        listInPrcnt3 = chngPercentList(Cl_last3_prd) #Volatility for last 3 candles
        stdev3 = round(sts.stdev(listInPrcnt3[1:]),2)
        stdev3Val = round(sts.stdev(Cl_last3_prd[1:]),2)
        #print('MTM(). Stdev3(%): ' + str(stdev3) + '; Stdev3(Val): ' + str(stdev3Val))

        mtmPrd[0], mtmPrd[1] = round((Cl_last-Cl_first)/Cl_last * 100,2), round(Cl_last-Cl_first,2)
        # if Cl_first < Cl_last:
        #     mtmPrdUp[0] = round((Cl_last-Cl_first)/Cl_last * 100,2)
        #     mtmPrdUp[1] = round(Cl_last-Cl_first,2)
        # if Cl_first > Cl_last:
        #     mtmPrdDn[0] = round((Cl_first-Cl_last)/Cl_first * 100,2)
        #     mtmPrdDn[1] = round(Cl_first-Cl_last,2)

        mtmLast20[0], mtmLast20[1] = round((Cl_last - Cl_last20)/Cl_last * 100, 2), round(Cl_last - Cl_last20, 2)
        # if Cl_last20 < Cl_last:
        #     mtmLast20Up[0] = round((Cl_last - Cl_last20)/Cl_last * 100, 2)
        #     mtmLast20Up[1] = round(Cl_last - Cl_last20, 2)
        # if Cl_last20 > Cl_last:
        #     mtmLast20Dn[0] = round((Cl_last20 - Cl_last)/Cl_last20 * 100, 2)
        #     mtmLast20Dn[1] = round(Cl_last20 - Cl_last, 2)

        mtmLast3[0], mtmLast3[1] = round((Cl_last - Cl_last3)/Cl_last * 100, 2), round(Cl_last - Cl_last3, 2)
        # if Cl_last3 < Cl_last:
        #     mtmLast3Up[0] = round((Cl_last - Cl_last3)/Cl_last * 100, 2)
        #     mtmLast3Up[1] = round(Cl_last - Cl_last3, 2)
        # if Cl_last3 > Cl_last:
        #     mtmLast3Dn[0] = round((Cl_last3 - Cl_last)/Cl_last3 * 100, 2)
        #     mtmLast3Dn[1] = round(Cl_last3 - Cl_last, 2)

        return mtmPrd, mtmLast20, mtmLast3, stdev, stdev10, stdev3
    except Exception as e:
        print('Exception from MTM ', e)

# Extremums on Klines for Period
def Extremums(H,L,C,O,dt_):
    #listCndlMinusPctUp, listCndlMinusPctDn = [],[] # list body candles - Percent% from Extemums
    bodyCO_Up,bodyCO_Dn = [],[] # body candles
    closeUp, closeDn ,bodyCndl_10 = [],[],[]
    #cnf.maxBdSubSetExtUp, cnf.maxBdSubSetExtDn,UpCount, DnCount = 0,0,0,0
    #ShdwUpTpBtm, ShdwDnTpBtm = [[], []], [[], []]  # List Shadows 0-Top 1-Bottom
    #ShdwUpTpBtmHlf, ShdwDnTpBtmHlf = [[], []], [[], []]  # List Shadows 0-Top 1-Bottom
    try:
        #mH = max(H)
        #mL = min(L)
        #H_half, L_half = H[-round(len(H)/2):],L[-round(len(L)/2):]
        #C_half, O_half = C[-round(len(C)/2):],O[-round(len(O)/2):]
        H_l10, L_l10 = H[-10:], L[-10:]
        C_l10, O_l10 = C[-10:], O[-10:]
# for period
        i=0
        for h,l,c,o,dtt in zip(H,L,C,O,dt_):
            if o < c:
                bodyCO_Up.append([i,round(c-o,4),round(((c-o)/c)*100,4),c,dtt])
                #bodyCO_Up.append([round(c-o,4),round(((c-o)/c)*100,4),c,dtt])
            if o > c:
                bodyCO_Dn.append([i,round(o-c,4),round(((o-c)/o)*100,4),c,dtt])
                #bodyCO_Dn.append([round(o - c, 4), round(((o - c) / o) * 100, 4), c, dtt])
            i+=1
# for half period
#         for h, l,c,o in zip(H_half, L_half,C_half,O_half):
#             #bodyCndl_hlf.append([round(h - l,4), round(((h - l) / h) * 100,4)])
#             if o < c:
#                 closeUp.append(c)
#                 bodyCndl_hlfUp.append([round(h-l,4),round(((h-l)/h)*100,4)])
#                 ShdwUpTpBtmHlf[0].append(round(h-c,2))
#                 ShdwUpTpBtmHlf[1].append(round(o-l,2))
#             if o > c:
#                 closeDn.append(c)
#                 bodyCndl_hlfDn.append([round(h-l,4),round(((h-l)/h)*100,4)])
#                 ShdwDnTpBtmHlf[0].append(round(h-o,2))
#                 ShdwDnTpBtmHlf[1].append(round(c-l,2))
# for last 10 period
        for h, l, c, o in zip(H_l10, L_l10, C_l10, O_l10):
            bodyCndl_10.append(round(abs(c - o),4))
            #if o < c:
            #    bodyCndl_10Up.append([round(h-l,4),round(((h-l)/h)*100,4)])
                #ShdwUpTpBtm[0].append(round(h-c,2))
                #ShdwUpTpBtm[1].append(round(o-l,2))
            #if o > c:
            #    bodyCndl_10Dn.append([round(l-h,4),round(((l-h)/l)*100,4)])
                #ShdwDnTpBtm[0].append(round(h-o,2))
                #ShdwDnTpBtm[1].append(round(c-l,2))

        avr10LastBody = round(sum(bodyCndl_10)/len(bodyCndl_10),2)
        #print('Extremums()... last 10 bodies/avr: ' + str(bodyCndl_10) + '/' + str(round(np.mean(bodyCndl_10),2)) + '; last 3 bodies/avr: ' + str(bodyCndl_10[-3:])+ '/' + str(avr3LastBody))
        #cnf.nLMTauto_GL = avr10LastBody
        #cnf.nLMTautoDn_GL = ShdwDnTopAvr #last 10 candles top shadows
        maxBodyCO_Up = max(bodyCO_Up, key=lambda x: x[1])
        maxBodyCO_Dn = max(bodyCO_Dn, key=lambda x: x[1])

#        cnf.maxBdSubSetExtUp = round(maxBodyCO_Up[2] - cnf.setExtremPercent, 2)

# 4.3 Create list from <maxBodyHL_Minus5_Up> - <listCndlMin5Up> PERIOD
#         for i, b in enumerate(bodyCO_Up):
#             if cnf.maxBdSubSetExtUp <= b[2]:# -5% from max
#                 UpCount += 1
#                 listCndlMinusPctUp.append(b) # Лист для эмуляции сделок в HSTREmulate profit_5
                #cnf.bigUpPercentNow[0] = round(sum([percent[2] for percent in listCndlMinusPctUp])/len(listCndlMinusPctUp),2)
                #if UpCount >= 7 and cnf.bigUpPercentNow[0] >= cnf.bigUpPercent[1]:  # if 3 candles about the same percent and current percent >= cnf.bigUpPercent
                #    cnf.bigUpPercent = cnf.bigUpPercentNow[0]
                    #print('\nExtremums()... UpCount >= 3  SUMlistCndlMinusPctUp:' + str(cnf.bigUpPercentNow)+ '\n')

 # 4.4 Create list from <maxBodyHL_Minus5_Dn> - <listCndlMin5Dn>
 #        cnf.maxBdSubSetExtDn = round(maxBodyCO_Dn[2] - cnf.setExtremPercent, 2)
 #        for i, b in enumerate(bodyCO_Dn):
 #            if cnf.maxBdSubSetExtDn <= b[2]:# -5% from max
 #                DnCount += 1
 #                listCndlMinusPctDn.append(b)

        return bodyCO_Up, bodyCO_Dn,maxBodyCO_Up,maxBodyCO_Dn, bodyCndl_10

    except Exception as e:
        print('Extremums()... Exception from Extremums ', e)

# Trend last n count KLines in sequence
def ShortTrend(Cl,O):
    UpFlag,DnFlag,BigUpFlag,BigDnFlag  = False,False,False,False
    try:
# check if Grow by default 3 candles get
        #mtmClUp = Cl[-1] - Cl[0] if Cl[0]<Cl[-1] else 0
        #mtmClDn = Cl[0] - Cl[-1] if Cl[0]>Cl[-1] else 0
# ----------------- if body last 3 candles change on X.XX percent --------------------------------------------------------
        cnf.Up3LastNow[0] = round((Cl[-1] - O[0])/Cl[-1] * 100,2) if O[0]< Cl[-1] else 0
        cnf.Up3LastNow[1] = round(Cl[-1] - O[0],2) if O[0]< Cl[-1] else 0
        cnf.Dn3LastNow[0] = round((O[0] - Cl[-1]) / O[0] * 100, 2) if O[0] > Cl[-1] else 0
        cnf.Dn3LastNow[1] = round(O[0] - Cl[-1], 2) if O[0] > Cl[-1] else 0
        if cnf.Up3LastNow[0] >= cnf.Up3LastSet: UpFlag = True
        if cnf.Dn3LastNow[0] >= cnf.Dn3LastSet: DnFlag = True
# ----------------- if last body candle change on X.XX percent --------------------------------------------------------
        Last_bodyUp = round((Cl[-1] - O[-1]) / Cl[-1] * 100,2) if O[-1] < Cl[-1] else 0 # body last candle Uprise in percent
        cnf.bigUpPercentNow[0],cnf.bigUpPercentNow[1] = Last_bodyUp, round(Cl[-1] - O[-1],2) if O[-1] < Cl[-1] else 0
        Last_bodyDn = round((O[-1] - Cl[-1]) / O[-1] * 100,2) if O[-1] > Cl[-1] else 0 # body last candle Down in perce
        cnf.bigDnPercentNow[0],cnf.bigDnPercentNow[1] = Last_bodyDn, round(O[-1] - Cl[-1], 2) if O[-1] > Cl[-1] else 0

        if Last_bodyUp > cnf.bigUpPercent: #if big Grow
            BigUpFlag = True
            #print("ShortTrend()... TRUE ShortTrend !!!!!!!!!!!!!!!!!! BigUp " + str(Last_bodyUp)[:4])
            #cnf.GrowOneBody.append([round(H[-1] - L[-1], 4), Last_bodyUp, dt_])

        if Last_bodyDn > cnf.bigDnPercent: # if body candle change on X.XX percent
            BigDnFlag = True
            #print("ShortTrend()... TRUE ShortTrend !!!!!!!!!!!!!!!!!! BigDn " + str(Last_bodyDn)[:4])
            #cnf.DnOneBody.append([round(H[-1] - L[-1], 4), Last_bodyDn, dt_])
            #rint('ShortTrend()... Down One Body data(list): ', cnf.DnOneBody)

        # print('\nShortTrend()... cnf.Up3LastNow/cnf.Up3LastSet: ' + str(cnf.Up3LastNow) + '/' + str(cnf.Up3LastSet))
        # print('ShortTrend()... cnf.Dn3LastNow/cnf.Dn3LastSet: ' + str(cnf.Dn3LastNow) + '/' + str(cnf.Dn3LastSet))
        # print('\nShortTrend()... bigUpPercent Set/Now: ' + str(cnf.bigUpPercent) + '/' + str(Last_bodyUp))
        # print('ShortTrend()... bigDnPercent Set/Now: ' + str(cnf.bigDnPercent) + '/' + str(Last_bodyDn))
        #print("---------------------------------------------------------------")
        # cnf.GrowOneBody = uniqueList(cnf.GrowOneBody)
        # #print('ShortTrend()... Grow One Body(list): ', cnf.GrowOneBody)
        # cnf.DnOneBody = uniqueList(cnf.DnOneBody)
        # #print('ShortTrend()... Down One Body data(list): ', cnf.DnOneBody)
        # cnf.GrowOnPeriod = uniqueList(cnf.GrowOnPeriod)
        # #print('ShortTrend()... Grow On Period(list): ', cnf.GrowOnPeriod)
        # cnf.DnOnPeriod = uniqueList(cnf.DnOnPeriod)
        # #print('ShortTrend()... Dn On Period(list): ', cnf.DnOnPeriod)

        return UpFlag, BigUpFlag, DnFlag, BigDnFlag #, round(mtmClUp,2), round(mtmClDn,2)

    except Exception as e:
        print('ShortTrend()Exception from ShortTrend', e)

def VolumeTrend(V):
    is_increase, is_decline, is_increase_1x3, is_decline_1x3 = False, False, False, False
    try:
       sumPeriod, sumPeriod_1x3 = [],[]
       volumeLast5 = V[-5:] # last 5 values
       sumLast5 = round(sum(volumeLast5),2) #sum last 5 candels
       sumPeriod.append(sumLast5) # last 5 candles
       sumPeriod_1x3.append(V[-1]) # last 1 candles
       #print('VolumeTrend()...         volumeLast5: ' + str(volumeLast10) + '; sum: ' + str(sumLast10))

       volumePenultPre5 = V[-10:-5] # last prp-enult 5 values
       sumPenultPre5 = round(sum(volumePenultPre5),2)
       sumPeriod.append(sumPenultPre5)
       #print('VolumeTrend()...    volumePenult10-5: '+ str(volumePenult10) + '; sum: ' + str(sumPenult10))

       volumePrePenultPrePre5 = V[-15:-10] # last pre-pre-penult 5 values
       sumprePenultPrePre5 = round(sum(volumePrePenultPrePre5),2)
       sumPeriod.append(sumprePenultPrePre5)

       is_increase_1x3 = all(i <= j for i, j in zip(V[-3:], V[-2:])) #if increase last 3 candles #SystemError: error return without exception set !!!!!!!

       is_decline_1x3 = all(i >= j for i, j in zip(V[-3:], V[-2:]))#if decline last 3 candles  #SystemError: error return without exception set !!!!!!!

       is_increase = all(i <= j for i, j in zip(sumPeriod, sumPeriod[1:]))#SystemError: error return without exception set !!!!!!!

       is_decline = all(i >= j for i, j in zip(sumPeriod, sumPeriod[1:])) #SystemError: error return without exception set !!!!!!!
    except Exception as e:
        print('Exception from VolumeTrend: ', e)

    return is_increase,is_decline, is_increase_1x3, is_decline_1x3

# Grow or Dawn MACD\Histogram
def MACDTrend(MACD, SIGNAL, HIST):
    histTop,histBtm, HIST_POS, HIST_NEG  = False,False,False,False
    if all(i > 0 for i in HIST):
        HIST_POS = True
    if all(i < 0 for i in HIST):
        HIST_NEG = True

    #print('MACDTrend()... HIST[0]: ' + str(HIST[0]) + '; HIST[1]: ' + str(HIST[1])+'; HIST[2]: ' + str(HIST[2]))
    if HIST_POS and (HIST[1] > HIST[0]) and (HIST[2]) > (HIST[1]):
        histTop = True
        #print('MACDTrend()... Histogram Grow: ' + str(histTop))
    elif HIST_NEG and (abs(HIST[1]) > abs(HIST[0])) and (abs(HIST[2]) > abs(HIST[1])):
            histBtm = True
            #print('MACDTrend()... Histogram Down: ' + str(histBtm))

    #print('MACDTrend()... HIST_POS: ' + str(HIST_POS) + '; HIST_NEG: ' + str(HIST_NEG))

    # if MACD below SIGNAL and hist Grow - buy
    #print('MACDTrend()... MACD: ' + str(MACD) +  '; SIGNAL: ' + str(SIGNAL) + '; histBtm: ' + str(histBtm))
    if (MACD < SIGNAL) and (MACD < 0) and histBtm:
        macd_buy = True
        #print('MACDTrend()... if MACD below SIGNAL: ' + str(macd_buy))
    else:
        macd_buy = False

    # if MACD above SIGNAL and hist Grow - sell
    if (MACD > SIGNAL) and (MACD > 0) and histTop:
        macd_sell = True
        #print('MACDTrend()... if MACD above SIGNAL: ' + str(macd_sell))
    else:
        macd_sell = False

    return macd_buy,macd_sell,HIST_POS,HIST_NEG

def uniqueList(list1):
    # intilize a null list
    unique_list = []
    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
            # print list
    return unique_list

#List Change in percent prev/curr = -/+0.0%
def chngPercentList(data):
    prev = 1
    listChangePrcnt = []
    for i, a in enumerate(data):
        listChangePrcnt.append((a / prev - 1) * 100)
        prev = a

    return listChangePrcnt



