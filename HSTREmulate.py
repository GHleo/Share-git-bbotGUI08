import tkinter as tk
from tkinter import messagebox as msg
from datetime import datetime as dt
import statistics as sts
import threading
import time
import configGlb as cnf
import ta
import AppEmulate as ae
import AppEmMargin as aem
import AppWork as app
import AppMargin as appm

from misc import macdSignalCross, HSTRmacdSignalCross

#Декоратор - выполнение функции в отдельный поток, без изменения остального кода
def thread(fn):
    def execute(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return execute

def run_progressbar(_pb00, delay_):
    _pb00["maximum"] = 100  # 4,5min
    for i in range(100):
        time.sleep(delay_)
        _pb00["value"] = i  # increment progressbar
        _pb00.update()  # have to call update() in loop

@thread
def HSTREm_algorithm(scrol01,scrol02, scrol03, scrol04, scrol05, scrolMain, pb00_, pb00, pb01,scrolShTr,scrolT2S1, scrolT2S2, scrolT2S3,pbT2S1,scrolT2S4,scrolT2S5, pbT2S2, scrolMACD):
    if not cnf.symbolPairGL:
        msg.showinfo("HSTREmulate", 'Please press button -> Init Pairs!')
        cnf.HSTRLoop_GL = False
    scrolMain.delete(0.1, tk.END)
#FFFF First variable Initialisation then will be auto init
    rcmUpMrg, rcmDnLng, Last10LngAvr, Last10MrgAvr, CalcProfit = ae.getInfo(scrolMain,scrolShTr, scrolMACD)
    if cnf.BigUpDn_CheckB == 1: #if selected Auto?
        cnf.bigUpPercent = rcmUpMrg
        cnf.bigDnPercent = rcmDnLng  # for Long
        cnf.Up3LastSet = round(rcmUpMrg * 1.5, 2)  # add 50% from rcmUpMrg. For Short
        cnf.Dn3LastSet = round(rcmDnLng * 1.5, 2)  # add 50% from rcmDnLng. For Long
    # cnf.bigUpPercent = rcmUpMrg
    # cnf.bigDnPercent = rcmDnLng  # for Long
    # cnf.Up3LastSet = round(rcmUpMrg * 1.5,2)  # add 50% from rcmUpMrg. For Short
    # cnf.Dn3LastSet = round(rcmDnLng * 1.5,2)  # add 50% from rcmDnLng. For Long
    cnf.nLMTautoDnLng_GL = Last10LngAvr #for Long
    cnf.nLMTautoUpMrg_GL = Last10MrgAvr #for Margin
    cnf.profitEm = CalcProfit
    print('cnf.bigUpPercent ' + str(cnf.bigUpPercent))
    print('Recommended For Margin:  cnf.bigUpPercent/cnf.Up3LastSet ' + str(rcmUpMrg) + '/' + str(cnf.Up3LastSet))
    print('Recommended For   Long:  cnf.bigDnPercent/cnf.Dn3LastSet ' + str(rcmDnLng) + '/' + str(cnf.Dn3LastSet))
    print('Recommended For   Profit:  nf.profitEm ' + str(CalcProfit))
    startTime = int(time.time())
    while cnf.HSTRLoop_GL:
        try:
            scrolMain.delete(0.1, tk.END)
            scrolShTr.delete(0.1, tk.END)
            scrolMACD.delete(0.1, tk.END)
            WeightIndexBuyShTr,WeightIndexSHORTShTr = 0,0 # index for Short Trend algoritm
            WeightIndexBuyMACD,WeightIndexSHORT_MACD = 0,0 # index based on Histrory algoritm
            #profit_u, profit_d, profitPrntUp, profitPrntDn = [0, 0, 0], [0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]
            klines = cnf.client.get_klines(symbol=cnf.symbolPairGL,interval=cnf.KlineGL,limit=cnf.KLINES_LIMITS)

            klinesMinusLast = klines[:len(klines) - int(cnf.USE_OPEN_CANDLES)]
            closes = [float(x[4]) for x in klinesMinusLast]
            opens = [float(x[1]) for x in klinesMinusLast]
            volume = [float(x[5]) for x in klinesMinusLast]
            closes_time = [float(x[6]) for x in klinesMinusLast]
            high = [float(x[2]) for x in klinesMinusLast]
            low = [float(x[3]) for x in klinesMinusLast]
            dt_ = [dt.fromtimestamp(round(x / 1000)) for x in closes_time]
            dt_HM = [dt.strftime(x, '%H:%M') for x in dt_]

            klinesMrg = cnf.client.get_klines(symbol=cnf.symbolPairGL, interval=cnf.KlineMrgGL, limit=cnf.KLINES_LIMITS)
            klinesMinusLastMrg = klinesMrg[:len(klinesMrg) - int(cnf.USE_OPEN_CANDLES)]
            closesMrg = [float(x[4]) for x in klinesMinusLastMrg]
            opensMrg = [float(x[1]) for x in klinesMinusLastMrg]
            highMrg = [float(x[2]) for x in klinesMinusLastMrg]
            lowMrg = [float(x[3]) for x in klinesMinusLastMrg]
            closes_timeMrg = [float(x[6]) for x in klinesMinusLastMrg]
            dt_Mrg = [dt.fromtimestamp(round(x / 1000)) for x in closes_timeMrg]
            dt_HM_Mrg = [dt.strftime(x, '%H:%M') for x in dt_Mrg]

            dt_Start = dt_[0].strftime('%H:%M')
            dt_End = dt_[len(dt_) - 1].strftime('%H:%M')
            price = float(cnf.client.get_symbol_ticker(symbol=cnf.symbolPairGL)['price'])
            macd, macdsignal, macdhist = ta.MACD(closes, 7, 14, 9)
            ui, di = macdSignalCross(macd, macdsignal)

            #ui, di = HSTRmacdSignalCross(macd, macdsignal, closes, high, low) # get values on crossed points
            macd_buy, macd_sell,HIST_POS,HIST_NEG = ta.MACDTrend(macd[-1], macdsignal[-1], macdhist[-3:]) # See Histogram
            mtmPrd, mtmLast20, mtmLast3,vlt,vlt10,vlt3, = ta.MTM(closes,price)# for intraday trading!!!!!!!!!
            isUp,isBigUp,isDn,isBigDn = ta.ShortTrend(closes[-int(cnf.fastMoveCount):],opens[-int(cnf.fastMoveCount):])

            get_ticker = cnf.client.get_ticker(symbol=cnf.symbolPairGL)
            priceChng24h = float(get_ticker['priceChangePercent'])
            #print('HSTREmulate.... priceChangePercent: ' + str(priceChng24h) + '; priceChange: ' + str(get_ticker['priceChange']))
            #print('HSTREmulate.... mtmPrd: ' + str(mtmPrd))
            priceChangeSet = 0.9
            if (priceChng24h and mtmPrd[0]) > priceChangeSet: # if grow UP trend !!!!!!!!!!!! DON't WORKING !!!!!!!!!!!!!!
                 #print('24h priceChangePercent Up Set/Now -> '+ str(priceChangeSet) +'/' + str(priceChng24h)+'; mtmPrd[0]' + str(mtmPrd[0]))
                 WeightIndexBuyShTr += 0.25
                 WeightIndexBuyMACD += 0.25
                 cnf.T[0] = 1
            if (priceChng24h and mtmPrd[0]) < (-priceChangeSet): # if Down trend
                 #print('24h priceChangePercen Down Set/Now -> '+ str(priceChangeSet) +'/' + str(priceChng24h)+'; mtmPrd[0]' + str(mtmPrd[0]))
                 WeightIndexSHORTShTr += 0.25
                 WeightIndexSHORT_MACD += 0.25
                 cnf.T[1] = 1
            #priceChange24h = cnf.bot.ticker24hr(symbol=cnf.symbolPairGL)
            #print('HSTREmulate.... bot.ticker24hr: ' + str(priceChange24h) + '\npriceChangePercent: ' + str(priceChange24h['priceChangePercent']))
            #print('HSTR... macd_buy: ' + str(macd_buy) + '; macd_sell: ' + str(macd_sell))
            if macd_buy: WeightIndexBuyMACD += 0.25  # if MACD below SIGNAL line and hist Grow
            if macd_sell: WeightIndexSHORT_MACD += 0.25 # if MACD above SIGNAL line and hist Grow
            if HIST_POS: WeightIndexSHORTShTr += 0.25 # if 3 last hist positive
            if HIST_NEG: WeightIndexBuyShTr += 0.25 # if 3 last hist negative

            increase, decline, increase1x3, decline1x3 = ta.VolumeTrend(volume) # last 45 minutes
            if increase:
                WeightIndexBuyShTr += 0.25
                WeightIndexSHORTShTr += 0.25
                WeightIndexBuyMACD += 0.25
                WeightIndexSHORT_MACD += 0.25

            if mtmLast20[0] > 0.5: # 0.5 in %
                WeightIndexSHORTShTr += 0.25 #in decline trend
                WeightIndexBuyMACD += 0.25 #in increase trend
            if mtmLast20[0] < -0.5: # 0.5 in %
                WeightIndexBuyShTr += 0.25 #in increase trend
                WeightIndexSHORT_MACD += 0.25 #in decline trend

#AAAAAAAAAAA Auto Init
            time_passedM = round((int(time.time()) - startTime) / 60, 2)
            if time_passedM > cnf.HSTR_LIFE_TIME_MIN: #Correcting -Delta for Limits($)- and bigUpPercent, bigDnPercent

                lBodyUp, _lstBodyDnLng, mBodyUp, mBodyDn, bodyCndl10Lng = ta.Extremums(high, low, closes,opens,dt_HM)  # for Long
                _lstBodyUpMrg, lBodyDn, mBodyUpMrg, mBodyDnMrg, bodyCndl10Mrg = ta.Extremums(highMrg, lowMrg,closesMrg,opensMrg,dt_HM_Mrg)  # for Margin
                # function for calculate cnf.bigUpPercent and cnf.bigDnPercent percent
                lstUp01, lstUp02, lstUp03, lstDn01, lstDn02, lstDn03, max_indexUpMrg, rcmUpMrg, max_indexDnLng, rcmDnLng = ae.listCndlMinPercents(_lstBodyUpMrg, _lstBodyDnLng)
                CalcProfit = ae.listHL_MinPercents(high, low, dt_HM, lBodyUp, _lstBodyDnLng, price) # get recomended profit

                startTime = int(time.time())
                if cnf.BigUpDn_CheckB == 1:  # if selected Auto?
                    cnf.bigUpPercent = rcmUpMrg
                    cnf.bigDnPercent = rcmDnLng  # for Long
                    cnf.Up3LastSet = round(rcmUpMrg * 1.5, 4)  # add 50% from rcmUpMrg. For Short
                    cnf.Dn3LastSet = round(rcmDnLng * 1.5, 4)  # add 50% from rcmDnLng. For Long
                #cnf.bigUpPercent = rcmUpMrg
                #cnf.bigDnPercent = rcmDnLng
                #cnf.Up3LastSet = round(rcmUpMrg * 1.5,4)  # add 50% from rcmUpMrg. For Short
                #cnf.Dn3LastSet = round(rcmDnLng * 1.5,4) # add 50% from rcmDnLng. For Long

                cnf.nLMTautoUpMrg_GL = round(sum(bodyCndl10Mrg)/len(bodyCndl10Mrg),2) # for Margin
                cnf.nLMTautoDnLng_GL = round(sum(bodyCndl10Lng)/len(bodyCndl10Lng),2) # for Long

                cnf.profitEm = CalcProfit
                print('HSTR... time_passedM: ' + str(time_passedM))
                print('Recommended For Margin:  cnf.bigUpPercent/cnf.Up3LastSet ' + str(rcmUpMrg) + '/' + str(cnf.Up3LastSet))
                print('Recommended For   Long:  cnf.bigDnPercent/cnf.Dn3LastSet ' + str(rcmDnLng) + '/' + str(cnf.Dn3LastSet))
# MACD MACD MACD MACD MACD MACD  -HISTORI if profit at Crossed Up for period - check ohter parameters and RUN algorithm SHORT TREND
            if ui: # and (tc_dicMax >= cnf.countTrade):
                WeightIndexBuyMACD += 0.25
                #cnf.log.debug("\n-MACD Up- macd_buy-> {macdbuy}; increase-> {inc}; mtmLast20U-> {mtm}; WeightIndexBuyMACD-> {wi}".format(macdbuy=macd_buy, inc=increase, mtm=mtmLast20U, wi=WeightIndexBuyMACD))
                if WeightIndexBuyMACD == 0.5:
                    #cnf.sellPercentCrdMACD_GL = selectMaxPercent(profit_u)
                    #cnf.sellSLPercentCrdMACD_GL = round(cnf.sellPercentCrdMACD_GL * 3,2)  # increase cnf.buyPercentShTr_GL
                    #cnf.log.debug("\n-MACD Up- macd_buy-> {macdbuy}; increase-> {inc}; mtmLast20-> {mtm}; WeightIndexBuyMACD-> {wi}".format(macdbuy=macd_buy, inc=increase, mtm=mtmLast20, wi=WeightIndexBuyMACD))
                    if cnf.driveMode == 0 and not cnf.eml_freezLong_GL and cnf.loop_AppEmul < cnf.loopGL and cnf.isMACD_GL:
                        cnf.eml_freezLong_GL = True  # flag for e_taTradeMACD
                        ae.e_taTradeMACD(scrol01,scrol02, scrol03, pb00)
                        print('HSTREmulate.... ae.e_taTradeMACD()')
                    elif cnf.driveMode == 1 and not cnf.App_freezLong_GL and cnf.loop_AppWrk < cnf.loopGL and cnf.isMACD_GL:
                        cnf.App_freezLong_GL = True  # flag for taTradeMACD
                        app.taTradeMACD(scrolT2S1, scrolT2S2, scrolT2S3,pbT2S1)
                        print('HSTREmulate.... app.taTradeMACD()')
                    # else:
                    #     print('HSTREmulate.... Ui some MESSAGE!!!!!!')
            if di: # and (tcd_dicMax >= cnf.countTrade):
                WeightIndexSHORT_MACD += 0.25
                #cnf.log.debug("\n-MACD Dn- macd_sell-> {macdsell}; increase-> {inc}; mtmLast20D-> {mtm}; WeightIndexSHORT_MACD-> {wi}".format(macdsell=macd_sell, inc=increase, mtm=mtmLast20D, wi=WeightIndexSHORT_MACD))
                if WeightIndexSHORT_MACD == 0.5:
                    #cnf.buyPercentCrdMACD_GL = selectMaxPercent(profit_d)
                    #cnf.buySLPercentCrdMACD_GL = round(cnf.buyPercentCrdMACD_GL * 3,2)  # increase cnf.buyPercentCrdMACD_GL
                    #cnf.log.debug("\n-MACD Dn- macd_sell-> {macdsell}; increase-> {inc}; mtmLast20D-> {mtm}; WeightIndexSHORT_MACD-> {wi}".format(macdsell=macd_sell, inc=increase, mtm=mtmLast20, wi=WeightIndexSHORT_MACD))
                    if cnf.driveMode == 0 and not cnf.eml_freezShort_GL and cnf.loop_AppEmMrg < cnf.loopMrgGL and cnf.isMACD_GL:
                        cnf.eml_freezShort_GL = True
                        aem.emrg_taTradeMACD(scrol01,scrol04, scrol05, pb01)
                        print('HSTREmulate.... aem.emrg_taTradeMACD')
                    elif cnf.driveMode == 1 and not cnf.AppMrg_freezShort_GL and cnf.loop_AppMrgMACD < cnf.loopMrgGL and cnf.isMACD_GL:
                        cnf.AppMrg_freezShort_GL = True
                        appm.mrgTradeMACD(scrolT2S1,scrolT2S4,scrolT2S5, pbT2S2)
                        print('HSTREmulate.... appm.mrgTradeMACD()')
                    # else:
                    #     print('HSTREmulate.... Di some MESSAGE!!!!!!')

# STREND STREND STREND STREND STREND -HISTORI if big Up/Dn or Up/Dn for period last 3 candles - check ohter parameters and RUN algorithm SHORT TREND
            if (isUp or isBigUp):
                #print('HSTREmulate.... isUp-> ' + str(isUp) + '; isBigUp-> ' + str(isBigUp) + '; cnf.isSTrend_G->' + str(cnf.isSTrend_GL) + '; cnf.isMACD_GL->' + str(cnf.isMACD_GL))
                WeightIndexSHORTShTr += 0.5
                #cnf.log.debug("\n-ShortTrend Dn- HIST_POS-> {macdsell}; increase-> {inc}; mtmLast20U-> {mtm}; WeightIndexSHORTShTr->{wi}".format(macdsell=HIST_POS, inc=increase, mtm=mtmLast20U, wi=WeightIndexSHORTShTr))
                if WeightIndexSHORTShTr >= 0.75:
                    #cnf.log.debug("\n-ShortTrend Dn- HIST_POS-> {macdsell}; increase-> {inc}; mtmLast20U-> {mtm}; WeightIndexSHORTShTr->{wi}".format(macdsell=HIST_POS, inc=increase, mtm=mtmLast20, wi=WeightIndexSHORTShTr))
                    #cnf.buyPercentShTr_GL = selectMaxPercent(profitPrntDn) # set profit percent
                    #cnf.buySLPercentShTr_GL = round(cnf.buyPercentShTr_GL * 3,2)  # double cnf.sellPercentShTr_GL
                    #cnf.isSTrend_GL = True  # take on flag isSTrend_GL when big Trend ???
                    if cnf.driveMode == 0 and not cnf.eml_freezShort_GL and cnf.loop_AppEmMrgShTr < cnf.loopMrgGL and cnf.isSTrend_GL:
                        cnf.eml_freezShort_GL = True  # take on flag isSTrend_GL when big Trend
                        aem.emrg_taTradeShTr(scrol01, scrol04, scrol05, pb01)
                        print('aem.emrg_taTradeShTr')
                    elif cnf.driveMode == 1 and not cnf.AppMrg_freezShort_GL and cnf.loop_AppMrgShTr < cnf.loopMrgGL and cnf.isSTrend_GL:
                        cnf.AppMrg_freezShort_GL = True
                        appm.mrgTradeShTr(scrolT2S1,scrolT2S4,scrolT2S5, pbT2S2)
                        print('HSTREmulate.... appm.mrgTradeShTr()')
                    else:
                        print('HSTREmulate.... Big Up some MESSAGE!!!!!!')
            if (isDn or isBigDn):# BUY if fast fall
                #print('HSTREmulate.... isDn-> ' + str(isDn) + '; isBigDn-> ' + str(isBigDn) + '; cnf.isSTrend_G->' + str(cnf.isSTrend_GL) + '; cnf.isMACD_GL->' + str(cnf.isMACD_GL))
                WeightIndexBuyShTr += 0.5
                #cnf.log.debug("\n-ShortTrend Up- HIST_NEG-> {macdbuy}; increase-> {inc}; mtmLast20D-> {mtm}; WeightIndexBuyShTr-> {wi}".format(macdbuy=HIST_NEG, inc=increase, mtm=mtmLast20D, wi=WeightIndexBuyShTr))
                if WeightIndexBuyShTr >= 0.75:
                    #cnf.sellPercentShTr_GL = selectMaxPercent(profitPrntUp) # set profit percent
                    #cnf.sellSLPercentShTr_GL = round(cnf.sellPercentShTr_GL * 3,2)  # double cnf.buyPercentShTr_GL
                    #cnf.log.debug("\n-ShortTrend Up- HIST_NEG-> {macdbuy}; increase-> {inc}; mtmLast20-> {mtm}; WeightIndexBuyShTr-> {wi}".format(macdbuy=HIST_NEG, inc=increase, mtm=mtmLast20, wi=WeightIndexBuyShTr))
                    #cnf.isSTrend_GL = True  # take on flag sSTrend_GL when big Trend ???
                    if cnf.driveMode == 0 and not cnf.eml_freezLong_GL and cnf.loop_AppEmulShTr < cnf.loopGL and cnf.isSTrend_GL:
                        cnf.eml_freezLong_GL = True
                        ae.e_taTradeShTrend(scrol01, scrol02, scrol03, pb00)
                    elif cnf.driveMode == 1 and not cnf.App_freezLong_GL and cnf.loop_AppWrkShTr < cnf.loopGL and cnf.isSTrend_GL:
                        cnf.App_freezLong_GL = True  # flag for taTradeMACD
                        app.taTradeShTrend(scrolT2S1, scrolT2S2, scrolT2S3, pbT2S1)
                        print('HSTREmulate.... app.taTradeShTrend()')
                    else:
                        print('HSTREmulate.... Big Dn some MESSAGE!!!!!!')

# AAAAAAAAAAAAAAAAAAAAA-HISTORI end algorithm SHORT TREND AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
            isTradesPOS = app.select4Tables(cnf.timeFrame,cnf.countPos)
            e_isTradesPOS, e_isTradesPOSall, e_prntNeg = ae.e_select4Tables(cnf.timeFrame,cnf.countPos, 25)

            l3Up, bUp = round(float(price) * cnf.Up3LastSet/100,2), round(float(price) * rcmUpMrg/100,2)
            l3Dn, bDn = round(float(price) * cnf.Dn3LastSet/100,2), round(float(price) * rcmDnLng/100,2)

            scrolMain.insert(tk.END, 'Pair - ' + str(cnf.symbolPairGL) +'; Period ->  ' + str(dt_Start) +' - '+ str(dt_End) + '\n\n')
            scrolMain.insert(tk.END, 'sum_PosTrades Up + Dn (items/value) Real-> ' + str(cnf.sum_PosTrades_Gl[0]) + '/' + str(cnf.sum_PosTrades_Gl[1])[:4] +'\nEmulation-> ' + str(cnf.sum_ePosTrades_Gl[0]) + '/' + str(cnf.sum_ePosTrades_Gl[1])[:4]+ '\n\n')
            sumNegUp_Dn = cnf.sum_NegTradesUp_Gl[0] + cnf.sum_NegTradesDn_Gl[0]
            sumValNegUp_Dn = cnf.sum_NegTradesUp_Gl[1] + cnf.sum_NegTradesDn_Gl[1]
            scrolMain.insert(tk.END, 'sum_NegTrades Up + Dn (items/value) Real-> ' + str(sumNegUp_Dn) + '/' + str(sumValNegUp_Dn)[:4] + '\nEmulation-> ' + str(cnf.sum_eNegTrades_Gl[0]) + '/' + str(cnf.sum_eNegTrades_Gl[1])[:4]+ '\n\n')

            #scrolMain.insert(tk.END, 'Select trades for last: ' + str(cnf.timeFrame) + '; Set value for positive trades: ' + str(cnf.countPos) + '\nis trades positive. Real = ' + str(isTradesPOS) + '; Emul = ' + str(e_isTradesPOS) + '\n')
            #scrolMain.insert(tk.END, 'EMULATION. % Negative trades(all must be >= 4); Set/Now-> 25%/' + str(e_prntNeg) + '\n\n')
            scrolMain.insert(tk.END, 'MTM Up/Dn for periods in candles and Volatility:' + '\n')
            scrolMain.insert(tk.END, ' 3  candles [%,Val]: ' + str(mtmLast3)+ '; Volatility-> ' + str(vlt3) + '\n')
            scrolMain.insert(tk.END, '20  candles [%,Val]: ' + str(mtmLast20) + '; Volatility-> ' + str(vlt10) + '\n' + str(cnf.KLINES_LIMITS) + ' candles [%,Val]: ' + str(mtmPrd) + '; Volatility-> ' + str(vlt) + '\n\n')
            scrolMain.insert(tk.END, 'Limits(avr last 10) Margin = ' + str(cnf.nLMTautoUpMrg_GL) + '$; Long = ' + str(cnf.nLMTautoDnLng_GL)+ '$\n\n')

            scrolMain.insert(tk.END, 'WeightIndexBuy(ShTr, MACD) +0,25 if -macd_buy-    true: ' + str(macd_buy)+ '\n')
            scrolMain.insert(tk.END, 'WeightIndexSHORT(ShTr, MACD) +0,25 if -macd_sell- true: ' + str(macd_sell)+ '\n')
            scrolMain.insert(tk.END, 'WeightIndex All +0,25 (last 9 min) if -increase-  true: ' + str(increase1x3) + '\n')
            scrolMain.insert(tk.END, 'WeightIndex All +0,25 (last 45 min) if -increase- true: ' + str(increase) + '\n')
            scrolShTr.insert(tk.END, 'WeightIndexBuyShTr  -> ' + str(WeightIndexBuyShTr) + '\nWeightIndexSHORTShTr-> ' + str(WeightIndexSHORTShTr) + '\n\n')
            scrolShTr.insert(tk.END, 'bigUpPercent, bigDnPercent and Limits change after: ' + str(round(cnf.HSTR_LIFE_TIME_MIN - time_passedM)) + ' min.\n\n')
            scrolShTr.insert(tk.END, 'Big Up (for Margin trade. Average last 101): \ncnf.bigUpPercent(Auto)-> ' + str(rcmUpMrg) + '/' + str(bUp) +'\nNow-> ' + str(cnf.bigUpPercentNow[0]) +'/' +str(cnf.bigUpPercentNow[1])+
                             '\n\nBig Down (for Long trade. Average last 101): \ncnf.bigDnPercent(Auto)-> ' + str(rcmDnLng) + '/' + str(bDn) +'\nNow-> '+ str(cnf.bigDnPercentNow[0]) + '/' + str(cnf.bigDnPercentNow[1]) +'\n\n')
            scrolShTr.insert(tk.END, 'Big Up Last N candles: \nAuto-> ' + str(cnf.Up3LastSet) + '/'  + str(l3Up) + '\nNow-> '  + str(cnf.Up3LastNow[0]) + '/' + str(cnf.Up3LastNow[1]) +
                             '\n\nBig Down Last N candles: \nAuto-> ' + str(cnf.Dn3LastSet) + '/' + str(l3Dn) + '\nNow-> ' + str(cnf.Dn3LastNow[0]) + '/' + str(cnf.Dn3LastNow[1]) + '\n\n')
            scrolMACD.insert(tk.END, 'WeightIndexBuyMACD    -> ' + str(WeightIndexBuyMACD) + '\nWeightIndexSHORT_MACD -> ' + str(WeightIndexSHORT_MACD) +'\n\n')

            thread = threading.Thread(target=run_progressbar(pb00_, 0.1))
            thread.start()
            if isTradesPOS and cnf.driveMode == 1: # or e_isTradesPOS or e_isProfit:
                #print('HSTREm_algorithm() Stop! isTradesPOS: ' + str(isTradesPOS) + '; e_isTradesPOS: ' + str(e_isTradesPOS) + '; e_isProfit: ' + str(e_isProfit))
                scrolMain.insert(0.1, 'HSTREm_algorithm() App Stop! Execute XX positive trades in sequence! ' + str(dt.now().strftime('%H:%M:%S'))+ '\n')
                cnf.HSTRLoop_GL = False
            if (e_isTradesPOS or e_isTradesPOSall) and cnf.driveMode == 0: # or e_isTradesPOS or e_isProfit:
                scrolMain.insert(0.1, 'HSTREm_algorithm() Emul Stop! Execute XX positive trades in sequence! ' + str(dt.now().strftime('%H:%M:%S'))+ '\n')
                cnf.HSTRLoop_GL = False

        except Exception as e:
            print("ERROR HSTREm_algorithm().... from WHILE cnf.HSTRLoop_GL {}".format(e))
            time.sleep(10)
            continue

# def MTM(Open,Close):
#     mtmOut = []
#     for o, c in zip(Open, Close):
#         mtmOut.append([round((c - o)/c *100, 2), round(c - o, 2)])
#         #mtmOut[1].append(round(o - c, 2))
#     print('MTM()... Open: ' + str(Open))
#     print('MTM()... Open: ' + str(sts.stdev))
#     print('MTM()... time frame 6 hours:  \nmtmOut: ' + str(mtmOut))
#     return mtmOut
# def selectMaxPercent(listProfit):
#     profit = {'0': 0.2, '1': 0.4, '2': 0.6, '3': 0.8, '4': 1}
#     maxItem = max(listProfit)
#     indexMaxItem = listProfit.index(maxItem)
#     profit_item = profit.get(str(indexMaxItem))
#
#     return profit_item




