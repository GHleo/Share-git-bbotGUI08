import tkinter as tk
from tkinter import messagebox as msg
from datetime import datetime as dt
import time
import sqlite3
import threading
import configGlb as cnf
import ta
import random
import queriesToDB as db
#from queriesToDB import (make_initial_table_emMRG,get_open_orders_emMRG,add_new_order_SELL_emMRG,make_initial_table_emMRG_ShTr,update_buy_order_emMRG)

from misc import adjust_to_step, macdSignalCross

limits = cnf.bot.exchangeInfo()  # Получаем лимиты пары с биржи

#Декоратор - выполнение функции в отдельный поток, без изменения остального кода
def thread(fn):
    def execute(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return execute

def run_progressbar(_pb00, delay_):
    _pb00["maximum"] = 100  # 4,5min
    for i in range(100):
        #time.sleep(cnf.chVarDelay_GL)
        time.sleep(delay_)
        _pb00["value"] = i  # increment progressbar
        _pb00.update()  # have to call update() in loop

@thread
def emrg_taTradeMACD(e1th_scrol,e4th_scrol,e5th_scrol,pb00_):
    # Устанавливаем соединение с локальной базой данных
    conn = sqlite3.connect('binance_app08.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    db.make_initial_table_emMRG(cursor)  # _taTrade
    global isBuing
    global isSelling
    if not cnf.symbolPairGL:
        msg.showinfo("AppEmulate", 'Please press button -> Init Pairs!')
    e5th_scrol.insert(tk.END, 'emrg_taTradeMACD() -> Start!!!' + '\n')
    while cnf.loop_AppEmMrg < cnf.loopMrgGL and cnf.eml_freezShort_GL: #
        try:
            db.get_open_orders_emMRG(cursor, cnf.symbolPairGL)
            order_statusS = True #
            isSelling, isBuing = True, True
            print('orders_infoEmMrg AppEmMargin-> ', cnf.orders_infoEmMrg)

# !!!!!!!!!!!!!!!! SOLD need BUY !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            if cnf.orders_infoEmMrg:
                print("Получены неисполненные ордера из БД: {orders}".format(orders=[(order, cnf.orders_infoEmMrg[order]['order_pair']) for order in cnf.orders_infoEmMrg]))
                delay_ = 0.05
                # datetime create BUY order  #dt.strptime(dtt, '%Y-%m-%d %H:%M:%S') -> to seconds -> dtt_.timestamp()  # преобразует строку в datetime
                while isBuing:
                    #print('while isBuing MACD MRG !!!!!!!!!!!!!!!')
                    bordID, bfordID, bamount, bsellprice, bneedprice, bfprice, bbalance, sorder, bincomeV,bincomeP, bprofit, bstoploss, bpairn, bcurrate, sdtSec, isBub = BUY(cnf.orders_infoEmMrg,'MACD') # -14-
                    time_passedM = round((int(time.time()) - sdtSec) / 60, 2)
                    e4th_scrol.delete(0.1, tk.END)
                    e4th_scrol.insert(tk.END, 'Buy... MACD MRG; Profit/StopLoss -> ' + str(bprofit) + '/' + str(bstoploss) + '\n' + 'Sold      -> ' + str(bsellprice) + '\n' + 'Curr rate         -> ' + str(
                                          bcurrate) + '\n' + 'Aim price -> ' + str(bneedprice) + '\n' + 'Forc sell -> ' + str(bfprice) + '\n' + 'Income(%) -> ' + str(bincomeP) + '\n' + str(cnf.BUYshrt_LIFE_TIME_MIN) + ' min. limit ..... time passed min. ' + str(time_passedM) + '\n')

                    print('Buy... MACD MRG Current rate: ' + str(bcurrate) + '; Buy price: ' + str(bneedprice))
# !!!!!!!!!!!!!!!!!!!!!! BUY MARKET with STOP LOSS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    if cnf.isMRKT_GL:
                        if time_passedM > cnf.BUYshrt_LIFE_TIME_MIN and isBub:
                            db.update_buy_order_emMRG(cursor, conn, bordID, sorder, bamount, bcurrate, bincomeV,1) # -8 -
                            e5th_scrol.insert(tk.END, 'BuyBUB... Price: ' + str(bcurrate) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '\nIncome($): ' + str(bincomeV) + '\n\n')
                            cnf.loop_AppEmMrg += 1
                            cnf.eml_freezShort_GL = False
                            break
                        if bcurrate <= bneedprice:
                            db.update_buy_order_emMRG(cursor, conn, bordID, sorder, bamount, bcurrate, bincomeV,1) # -8 -
                            e5th_scrol.insert(tk.END, 'Buy... Price: ' + str(bcurrate) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '\nIncome($): ' + str(bincomeV) + '\n\n')
                            cnf.loop_AppEmMrg += 1
                            cnf.eml_freezShort_GL = False
                            break
                        if bfprice <= bcurrate and bstoploss > 0:
                            db.update_buy_order_emMRG(cursor, conn, bfordID, sorder, bamount, bcurrate, bincomeV,0) # -8 -
                            e5th_scrol.insert(tk.END, 'Force Buy... Price: ' + str(bcurrate) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '\nIncome($): ' + str(bincomeV)+ '\n\n')
                            cnf.loop_AppEmMrg += 1
                            cnf.eml_freezShort_GL = False
                            break
# !!!!!! !!!!!!!!!!!!!!!! BUY LIMIT with STOP LOSS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    if cnf.isLMT_GL:
                        if time_passedM > cnf.BUYshrt_LIFE_TIME_MIN and isBub:
                            db.update_buy_order_emMRG(cursor, conn, bordID, sorder, bamount, bcurrate, bincomeV, 1)  # -8 -
                            e5th_scrol.insert(tk.END,'BuyBUB... Price: ' + str(bcurrate) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '; Time passed min-> '+ str(time_passedM) + '\nIncome($)-> ' + str(bincomeV)+ '\n\n')
                            cnf.loop_AppEmMrg += 1
                            cnf.eml_freezShort_GL = False
                            break
                        if bcurrate <= bneedprice:
                            db.update_buy_order_emMRG(cursor, conn, bordID, sorder, bamount, bcurrate, bincomeV, 1)  # -8 -
                            e5th_scrol.insert(tk.END,'Buy... Price: ' + str(bcurrate)+ '; ' + str(dt.now().strftime('%H:%M:%S')) + '; Time passed min-> '+ str(time_passedM)  + '\nIncome($)-> ' + str(bincomeV) + '\n\n')
                            cnf.loop_AppEmMrg += 1
                            cnf.eml_freezShort_GL = False
                            break
                        if cnf.isLMT_GL and bfprice < bcurrate and bstoploss > 0:
                            db.update_buy_order_emMRG(cursor, conn, bordID, sorder, bamount, bcurrate, bincomeV, 0)  # -8 -
                            e5th_scrol.insert(tk.END,'Force Buy... Price: ' + str(bcurrate)+ '; ' + str(dt.now().strftime('%H:%M:%S')) + '; Time passed min-> '+ str(time_passedM)  + '\nIncome($)-> ' + str(bincomeV) + '\n\n')
                            cnf.loop_AppEmMrg += 1
                            cnf.eml_freezShort_GL = False
                            break
                    thread = threading.Thread(target=run_progressbar(pb00_, delay_))
                    thread.start()

# !!!!!!!!!!!!!!!! SELLING  Если остались пары, по которым нет текущих торгов !!!!!!!!!!!!!!!!!!!!!
            else:
                while isSelling and cnf.eml_freezShort_GL:
                    klines = cnf.bot.klines(symbol=cnf.symbolPairGL,interval=cnf.KlineMrgGL,limit=cnf.KLINES_LIMITS)
                    klinesMinusLast = klines[:len(klines) - int(cnf.USE_OPEN_CANDLES)]
                    closes = [float(x[4]) for x in klinesMinusLast]
                    cprice = str(cnf.bot.tickerPrice(symbol=cnf.symbolPairGL)['price'])[:7]
                    macd, macdsignal, macdhist = ta.MACD(closes, 7, 14, 9)
                    Ups, Dns = macdSignalCross(macd, macdsignal)  # MACD line crosses the signal line Up or Down

                    if not cnf.is_taTrade:
                        cnf.is_mrgTradeEm = True  # emrg_taTradeShTr is working
                        e1th_scrol.delete(0.1, tk.END)
                        e1th_scrol.insert(tk.END,'# Emulating MACD cross Down (emrg_taTradeMACD) #' + '\n' + '      (When Buing in progress it freez!) ' + '\n\n')
                        e1th_scrol.insert(tk.END,'MACD -> EMA Short/Long/Signal -> 7/14/9' + '\n\n' + 'KLINES_LIMITS(period)-> ' + str(cnf.KLINES_LIMITS) + '\n' + 'TIMEFRAME(in minutes)-> ' + str(cnf.KlineMrgGL) + '\n')
                        e1th_scrol.insert(tk.END, 'Sell LIFE_TIME_MIN -> ' + str(cnf.SELLshrt_LIFE_TIME_MIN) + '\n' + 'Buy LIFE_TIME_MIN  -> ' + str(cnf.BUYshrt_LIFE_TIME_MIN) + '\n')
                        e1th_scrol.insert(tk.END, '---------------------------------------------\n\n'+ str(dt.fromtimestamp(int(time.time()))) + '\n')
                        e1th_scrol.insert(tk.END, 'Is Market/Limit?         -> ' + str(cnf.isMRKT_GL) + '/' + str(cnf.isLMT_GL) + '\n' + 'Is cross Dn signal line? -> ' + str(Dns) + '\n' + 'Rate             -> ' + str(cprice) + '\n')
                        e1th_scrol.insert(tk.END, '---------------------------------------------' + '\n')
# !!!!!!!!!!!!!!!!!!!!!! SELL MARKET - MACD - if signal line crossed !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    if Dns and cnf.isMRKT_GL:  # if MACD cross signal lane OR started from HSTREmulate and Market
                        pname, orderID, myamount, spendsum, profitmarkup, stoploss, currate, dts = SELL('MACD') # -8-
                        db.add_new_order_SELL_emMRG(cursor, conn, pname, orderID, myamount, currate, spendsum, profitmarkup, stoploss,'market') # -9-
                        e5th_scrol.insert(tk.END, 'Sell... MACD MRG -MARKET- Pair: ' + str(pname) + '\nPrice: ' + str(currate) + '; Amount: ' + str(myamount) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                        break  # terminate loop -isBuing-
# !!!!!!!!!!!!!!!!!!!!!! SELL LIMIT with TIMER - MACD - if signal line crossed !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    if Dns and cnf.isLMT_GL:  # if Short trend or started from HSTREmulate and Limit
                        spname, sorderID, smyamount, sspendsum, sprofitmarkup, sstoploss, scurrate, sdts = SELL('MACD')  # -8-
                        need_priceLMT = round(scurrate + cnf.nLMTautoUpMrg_GL,2) # cost for limit order
                        while order_statusS:
                            curr_rate = float(cnf.bot.tickerPrice(symbol=cnf.symbolPairGL)['price'])
                            time_passedM = round((int(time.time()) - sdts)/60,2)
                            e4th_scrol.delete(0.1, tk.END)
                            e4th_scrol.insert(tk.END, 'Sell... MACD -LIMIT- Current rate -> ' + str(curr_rate)+ '\nAim -> ' + str(need_priceLMT) + '\n..... time passed min. ' + str(time_passedM) + '\n')
                            if time_passedM > cnf.SELLshrt_LIFE_TIME_MIN:  # if time passed Exit from loop -order_statusB-
                                e5th_scrol.insert(tk.END, 'Sell... MACD -LIMIT-  Pair: ' + str(spname) + '; time_passed min-> ' + str(time_passedM) + '; cnf.nLMTautoUpMrg_GL: ' + str(cnf.nLMTautoUpMrg_GL)+ ' ****** EXIT ******' + '\n\n')
                                isSelling = False
                                cnf.eml_freezShort_GL = False
                                print('!!!! emrg_taTradeMACD... currate: ' + str(curr_rate) + '; cnf.nLMTautoUpMrg_GLL: ' + str(cnf.nLMTautoUpMrg_GL))
                                break  # terminate loop -order_statusB-
                            if curr_rate >= need_priceLMT:
                                db.add_new_order_SELL_emMRG(cursor, conn, spname, sorderID, smyamount, curr_rate, sspendsum, sprofitmarkup, sstoploss,'limit') # -9-
                                e5th_scrol.insert(tk.END, 'Sell... MACD MRG -LIMIT- Pair: ' + str(spname) + '\nPrice: ' + str(need_priceLMT) + '; Amount: ' + str(smyamount) + '; cnf.nLMTautoUpMrg_GL: ' + str(cnf.nLMTautoUpMrg_GL) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                isSelling = False
                                print('!!!! emrg_taTradeMACD... currate: ' + str(curr_rate) + '; cnf.nLMTautoUpMrg_GL: ' + str(cnf.nLMTautoUpMrg_GL))
                                break
                    if not isSelling: break  # Exit from loop isSelling
                    thread = threading.Thread(target=run_progressbar(pb00_, cnf.chVarDelay_GL))
                    thread.start()
            cnf.is_mrgTradeEm = False  # emrg_taTradeMACD is not working
            if cnf.loop_AppEmMrg >= cnf.loopMrgGL:  # Enable loop for HSTR Emulate for cross Up
                e4th_scrol.insert(tk.END, 'emrg_taTradeMACD TERMINATE! Loop = ' + str(cnf.loop_AppEmMrg) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                cnf.eml_freezShort_GL = False
        except Exception as e:
            print("ERROR emrg_taTradeMACD().... from WHILE cnf.loop_AppEmMrg {} ".format(e))
            e4th_scrol.insert(tk.END,'ERROR!!!!!!! emrg_taTradeMACD().... from WHILE cnf.loop_AppEmMrg' + str(e) + '\n')
            time.sleep(10)
            continue
    e4th_scrol.insert(tk.END, 'emrg_taTradeMACD TERMINATE - End Function!  loop_AppEmMrg = ' + str(cnf.loop_AppEmMrg) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
    cursor.close()
@thread
def emrg_taTradeShTr(e1th_scrol,e4th_scrol,e5th_scrol,pb00_):
    conn = sqlite3.connect('binance_app08.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    db.make_initial_table_emMRG_ShTr(cursor)  #
    print('emrg_taTradeShTr START !!!!!!!!!!!!!!!!! ')
    global isBuing
    global isSelling
    if not cnf.symbolPairGL:
        msg.showinfo("AppEmulate", 'Please press button -> Init Pairs!')
    e5th_scrol.insert(tk.END, 'emrg_taTradeShTr() -> Start!!!' + '\n')
    while cnf.loop_AppEmMrgShTr < cnf.loopMrgGL and cnf.eml_freezShort_GL:
        try:
            #db.test(cursor, conn, 333,644, 10, 0.9, -27, 1)
            db.get_open_orders_emMRG_ShTr(cursor)
            order_statusS = True
            isBuing = True
            isSelling = True
            print('orders_infoEmMrgShTr AppEmMargin-> ', cnf.orders_infoEmMrgShTr)
# !!!!!!!!!!!!!!!! SOLD need BUY !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            if cnf.orders_infoEmMrgShTr:
                print("Получены неисполненные ордера из БД: {orders}".format(orders=[(order, cnf.orders_infoEmMrgShTr[order]['order_pair']) for order in cnf.orders_infoEmMrgShTr]))
                delay_ = 0.05
                while isBuing:
                    print('while isBuing Short Trend MRG !!!!!!!!!!!!!!!')
                    bordID, bfordID, bamount, bsellprice, bneedprice, bfprice, bbalance, sorder, bincomeV,incomeP, bprofit, bstoploss, bpairn, bcurrate, sdtSec, isBub = BUY(cnf.orders_infoEmMrgShTr,'ShortTrend')  # -14-
                    time_passedM = round((int(time.time()) - sdtSec) / 60, 2)
                    e4th_scrol.delete(0.1, tk.END)
                    e4th_scrol.insert(tk.END, 'Buy... Short Trend MRG; Profit/StopLoss -> ' + str(bprofit) + '/' + str(bstoploss) + '\nSold      -> ' + str(bsellprice) + '\nCurr rate ->        ' + str(
                        bcurrate) + '\nAim price -> ' + str(bneedprice) + '\nForc sell -> ' + str(bfprice) + '\nIncome(%) -> ' + str(incomeP) + '\n..... time passed min. ' + str(time_passedM) + '\n')
# !!!!!!!!!!!!!!!!!!!!!! BUY MARKET with STOP LOSS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    if cnf.isMRKT_GL:
                        if time_passedM > cnf.BUYshrt_LIFE_TIME_MIN and isBub:
                            db.update_buy_order_emMRG_ShTr(cursor, conn, bordID, sorder, bamount, bcurrate, bincomeV,1)  # -8 -
                            e5th_scrol.insert(tk.END, 'BuyBub... Price: ' + str(bcurrate) + '; ' + str(dt.now().strftime('%H:%M:%S'))  + '\nIncome($)-> ' + str(bincomeV) + '\n\n')
                            cnf.eml_freezShort_GL = False  # to proceed at HSTREmulate
                            cnf.loop_AppEmMrgShTr += 1
                            break
                        if bcurrate <= bneedprice:
                            db.update_buy_order_emMRG_ShTr(cursor, conn, bordID, sorder, bamount, bcurrate, bincomeV, 1)  # -8 -
                            e5th_scrol.insert(tk.END,'Buy... Price: ' + str(bcurrate) + str(bincomeV) + '; ' + str(dt.now().strftime('%H:%M:%S'))  + '\nIncome($)-> ' + '\n\n')
                            cnf.eml_freezShort_GL = False # to proceed at HSTREmulate
                            cnf.loop_AppEmMrgShTr += 1
                            break
                        if (bfprice <= bcurrate) and (bstoploss > 0):
                            db.update_buy_order_emMRG_ShTr(cursor, conn, bfordID, sorder, bamount, bcurrate, bincomeV,0)  # -8 -
                            e5th_scrol.insert(tk.END, 'Force buy... Price: ' + str(bcurrate) + str(bincomeV) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '\nIncome($)-> ' + '\n\n')
                            cnf.eml_freezShort_GL = False  # to proceed at HSTREmulate
                            cnf.loop_AppEmMrgShTr += 1
                            break

# !!!!!!!!!!!!!!!!!!!!!! BUY LIMIT with STOP LOSS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    if cnf.isLMT_GL:
                        if time_passedM > cnf.BUYshrt_LIFE_TIME_MIN and isBub:
                            db.update_buy_order_emMRG_ShTr(cursor, conn, bfordID, sorder, bamount, bcurrate, bincomeV,1)  # -8 -
                            e5th_scrol.insert(tk.END,'BuyBub... Price: ' + str(bcurrate) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '; Time passed min.->' + str(time_passedM) + '\nIncome($)-> ' + str(bincomeV) + '\n\n')
                            cnf.eml_freezShort_GL = False  # to proceed at HSTREmulate
                            cnf.loop_AppEmMrgShTr += 1
                            break
                        if bcurrate <= bneedprice:
                            db.update_buy_order_emMRG_ShTr(cursor, conn, bfordID, sorder, bamount, bcurrate, bincomeV,1)  # -8 -
                            e5th_scrol.insert(tk.END,'Buy... Short Trend MRG -LIMIT- Price: ' + str(bcurrate) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '; Time passed min.->' + str(time_passedM) + '\nIncome($)-> ' + str(bincomeV) + '\n\n')
                            cnf.eml_freezShort_GL = False  # to proceed at HSTREmulate
                            cnf.loop_AppEmMrgShTr += 1
                            break
                        if bfprice < bcurrate and bstoploss > 0:
                            db.update_buy_order_emMRG_ShTr(cursor, conn, bfordID, sorder, bamount, bcurrate, bincomeV,1)  # -8 -
                            e5th_scrol.insert(tk.END, 'Force Buy... Short Trend MRG -LIMIT- Price: ' + str(bcurrate) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '; Time passed min.->' + str(time_passedM) + '\nIncome($)-> ' + str(bincomeV)+ '\n\n')
                            cnf.eml_freezShort_GL = False  # to proceed at HSTREmulate
                            cnf.loop_AppEmMrgShTr += 1
                            break

                    thread = threading.Thread(target=run_progressbar(pb00_, delay_))
                    thread.start()
# !!!!!!!!!!!!!!!!!!!!!!! SELLING  Если остались пары, по которым нет текущих торгов !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            else:
                while isSelling and cnf.eml_freezShort_GL:
                    klines = cnf.bot.klines(symbol=cnf.symbolPairGL, interval=cnf.KlineMrgGL, limit=cnf.KLINES_LIMITS)
                    klinesMinusLast = klines[:len(klines) - int(cnf.USE_OPEN_CANDLES)]
                    opens = [float(x[1]) for x in klinesMinusLast]
                    closes = [float(x[4]) for x in klinesMinusLast]
                    cprice = str(cnf.bot.tickerPrice(symbol=cnf.symbolPairGL)['price'])[:7]
                    isUp, isBigUp, isDn, isBigDn = ta.ShortTrend(closes[-int(cnf.fastMoveCount):],opens[-int(cnf.fastMoveCount):])

                    if not cnf.is_taTrade:
                        cnf.is_mrgTradeEm = True  # emrg_taTradeShTr is working
                        e1th_scrol.delete(0.1, tk.END)
                        e1th_scrol.insert(tk.END, '## Emulating ShortTrend Down (emrg_taTradeShTr) ##' + '\n' + '      (When Buing in progress it freez!) ' + '\n\n')
                        e1th_scrol.insert(tk.END, 'KLINES_LIMITS(period) -> ' + str(cnf.KLINES_LIMITS) + '\n' + 'TIMEFRAME(in minutes) -> ' + str(cnf.KlineMrgGL) + '\n')
                        e1th_scrol.insert(tk.END, 'Sell  LIFE_TIME_MIN -> ' + str(cnf.SELLshrt_LIFE_TIME_MIN) + '\n' + 'Buy LIFE_TIME_MIN   -> ' + str(cnf.BUYshrt_LIFE_TIME_MIN) + '\n')
                        e1th_scrol.insert(tk.END, '---------------------------------------------\n\n' + str(dt.fromtimestamp(int(time.time()))) + '\n')
                        e1th_scrol.insert(tk.END, 'Is Market/Limit?           -> ' + str(cnf.isMRKT_GL) + '/' + str(cnf.isLMT_GL) + '\n' + 'Is 3 candles Grow/Down?    -> ' + str(isUp) + '/' + str(isDn) + '\n' + 'Is last candle Grow/Down? -> ' + str(isBigUp) + '/' + str(isBigDn) + '\n')
                        e1th_scrol.insert(tk.END,  'Rate      -> ' + str(cprice) + '\n'+ '---------------------------------------------' + '\n')
# !!!!!!!!!!!!!!!!!!!!!! SELL MARKET if fast Grow last candel !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    if (isUp or isBigUp) and cnf.isMRKT_GL:  # if SHORT TREND or STARTED from HSTREmulate and Market
                        print('Sell(Mrg)... ShortTrend -MARKET-  if isUp {iu} isBigUp {ibu} isMRKT_GL  {m}'.format(iu=isUp, ibu=isBigUp, m=cnf.isMRKT_GL))
                        pname, orderID, myamount, spendsum, profitmarkup, stoploss, currate, dts = SELL('ShortTrend') # -8-
                        db.add_new_order_SELL_emMRG_ShTr(cursor, conn, pname, orderID, myamount, currate, spendsum, profitmarkup, stoploss,'market') # -9-
                        e5th_scrol.insert(tk.END, 'Short Trend MRG -MARKET- Pair: ' + str(pname) + '\nSell.. Price: ' + str(currate) + '; Amount: ' + str(myamount) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                        #isSelling = False
                        break  # terminate loop -isBuing-
# !!!!!!!!!!!!!!!!!!!!!! SELL LIMIT with TIMER - MACD - if signal line crossed !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    if (isUp or isBigUp) and cnf.isLMT_GL:  # if Short trend or started from HSTREmulate and Limit
                        spname, sorderID, smyamount, sspendsum, sprofitmarkup, sstoploss, scurrate, sdts = SELL('ShortTrend')  # -8-
                        while order_statusS:
                            curr_rate = round(float(cnf.bot.tickerPrice(symbol=cnf.symbolPairGL)['price']),2)
                            need_priceLMT = round(scurrate + cnf.nLMTautoUpMrg_GL,2)
                            time_passedM = round((int(time.time()) - sdts) / 60, 2)
                            e4th_scrol.delete(0.1, tk.END)
                            e4th_scrol.insert(tk.END, 'Sell... Short Trend -LIMIT- Current rate -> ' + str(curr_rate) + '\nAim -> ' + str(need_priceLMT) + '\n..... time passed min. ' + str(time_passedM) + '\n')
                            if time_passedM > cnf.SELLshrt_LIFE_TIME_MIN:
                                e5th_scrol.insert(tk.END, 'Short Trend MRG -LIMIT- Pair: ' + str(spname) + '; time_passed min-> ' + str(time_passedM)+ '; cnf.nLMTautoUpMrg_GL: ' + str(cnf.nLMTautoUpMrg_GL) + ' ****** EXIT ******' + '\n\n')
                                isSelling = False
                                cnf.eml_freezShort_GL = False
                                print('!!!! emrg_taTradeShTr... currate: ' + str(curr_rate) + '; cnf.nLMTautoUpMrg_GL:' + str(cnf.nLMTautoUpMrg_GL))
                                break  # terminate loop -order_statusB-
                            if curr_rate >= need_priceLMT:
                                db.add_new_order_SELL_emMRG_ShTr(cursor, conn, spname, sorderID, smyamount, curr_rate, sspendsum, sprofitmarkup, sstoploss,'limit')  # -9-
                                e5th_scrol.insert(tk.END, 'Short Trend MRG -LIMIT- Pair: ' + str(spname) + '\nSell.. Price: ' + str(need_priceLMT) + '; Amount: ' + str(smyamount) + '; cnf.nLMTautoUpMrg_GL: ' + str(cnf.nLMTautoUpMrg_GL)+ '; ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                isSelling = False
                                print('!!!! emrg_taTradeShTr... currate: ' + str(curr_rate) + '; cnf.nLMTautoUpMrg_GL: ' + str(cnf.nLMTautoUpMrg_GL))
                                break
                    if not isSelling: break  # Exit from loop isSelling

                    thread = threading.Thread(target=run_progressbar(pb00_, cnf.chVarDelay_GL))
                    thread.start()
            cnf.is_mrgTradeEm = False  # emrg_taTradeShTr is not working
            if cnf.loop_AppEmMrgShTr >= cnf.loopMrgGL:  # Enable loop for HSTR Emulate for cross Up
                e4th_scrol.insert(tk.END, 'emrg_taTradeShTr TERMINATE! Loop = ' + str(cnf.loop_AppEmMrgShTr) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                cnf.eml_freezShort_GL = False

        except Exception as e:
            print("ERROR emrg_taTradeShTr().... from WHILE cnf.loop_AppEmMrgShTr {}".format(e))
            #print('testSQLiteGlb: ' + str(cnf.testSQLiteGlb) + '\n')
            #cnf.taTradeMMRGBtn_GL = False
            time.sleep(10)
            continue
    e4th_scrol.insert(tk.END, 'emrg_taTradeShTr TERMINATE - End Function!  loop_AppEmMrgShTr = ' + str(cnf.loop_AppEmMrgShTr) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
    cursor.close()
def BUY(orders_info,b_algorithm):
    isBub = False
    for order, value in orders_info.items():
        try:
            # if cnf.eml_freezShort_GL and (b_algorithm == 'ShortTrend'):
            #     profit_markup = cnf.buyPercentShTr_GL
            #     stloss = cnf.buySLPercentShTr_GL
            # elif cnf.eml_freezShort_GL and (b_algorithm == 'MACD'):
            #     profit_markup = cnf.buyPercentCrdMACD_GL
            #     stloss = cnf.buySLPercentCrdMACD_GL
            # else:
            #     profit_markup = round(cnf.pairsGL[value['order_pair']]['profit_markup'],4)
            #     stloss = value['panic_fee']
            profit_markup = round(cnf.pairsGL[value['order_pair']]['profit_markupMrg'],4)
            stloss = value['panic_fee']
                            # смотрим, какие ограничения есть для создания ордера на продажу
            for elem in limits['symbols']:
                if elem['symbol'] == value['order_pair']:
                    CURR_LIMITS = elem
                    break
            else:
                raise Exception("BUY() Не удалось найти настройки выбранной пары " + value['order_pair'])

            if value['panic_fee'] > 0:
                fbuy_price = round(value['sell_price'] * (100 + value['panic_fee']+0.15) / 100,2)
            else:
                fbuy_price = 0

            got_qty =value['sell_amount']
            # Рассчитываем минимальную сумму, которую нужно получить, что бы остаться в плюсе ЗА ВЫЧЕТОМ ПРОЦЕНТА при продаже без BNB
            need_cost = round((got_qty * value['sell_price'] * (1 - profit_markup / 100 - 0.0015)) / got_qty,2)

            # Берем цены покупок (нужно будет продавать по рынкду)
            curr_rate = round(float(cnf.bot.tickerPrice(symbol=value['order_pair'])['price']), 2)
            incomeV = round((got_qty * value['sell_price']) * (1 - 0.00075) - (got_qty * curr_rate) * (1 - 0.00075),2)  # commission 0.075%
            incomeP = round((value['sell_price']/curr_rate  - 1) * 100, 2)

            ForderID = random.random()
            SorderID = random.random()

            bub = value['sell_price'] * (1 - 0.0015)
            if curr_rate < bub:
                isBub = True
            sellDate = dt.strptime(value['sell_created'],'%Y-%m-%d %H:%M:%S')  # преобразует строку в datetime; timestamp() - возвращает время в секундах с начала эпохи.
            sellDateSec = sellDate.timestamp()
            return SorderID, ForderID, value['sell_amount'], value['sell_price'], need_cost, fbuy_price, value['balance'], order, incomeV, incomeP,profit_markup, stloss, value['order_pair'], curr_rate,sellDateSec,isBub

        except Exception as e:
            print("Error from BUY()... in AppEmMargin {}".format(e))


def SELL(algorithm):
    # Если остались пары, по которым нет текущих торгов
    if cnf.pairsGL:
        try:
            for pair_name, pair_obj in cnf.pairsGL.items():
                # if cnf.eml_freezShort_GL and (algorithm == 'ShortTrend'):
                #     profit = cnf.buyPercentShTr_GL
                #     stloss = cnf.buySLPercentShTr_GL
                # elif cnf.eml_freezShort_GL and (algorithm == 'MACD'):
                #     profit = cnf.buyPercentCrdMACD_GL
                #     stloss = cnf.buySLPercentCrdMACD_GL
                # else:
                #     profit = pair_obj['profit_markup']
                #     stloss = pair_obj['stop_loss']
                profit = pair_obj['profit_markupMrg']
                stloss = pair_obj['stop_lossMrg']
                print("SELL() Работаем с парой {pair}".format(pair=pair_name))
                for elem in limits['symbols']:
                    if elem['symbol'] == pair_name:
                        CURR_LIMITS = elem
                        break
                else:
                    raise Exception("SELL()... Не удалось найти настройки выбранной пары " + pair_name)
                balances_mrg = 1000  # mrgAccount['totalAssetOfBtc']
                # Если баланс позволяет торговать - выше лимитов биржи и выше указанной суммы в настройках
                if balances_mrg >= pair_obj['spend_sum_mrg']:
                    #prices = cnf.bot.tickerBookTicker(symbol=pair_name)
                    # Берем цены продаж (продажа будет по рынку)
                    #top_price = float(prices['bidPrice'])
                    top_price = round(float(cnf.bot.tickerPrice(symbol=pair_name)['price']), 2)
                    #print("SELL() top_price ",top_price)
                    spend_sum = pair_obj['spend_sum_mrg']
                    #print("SELL() spend_sum ",spend_sum)
                    # Рассчитываем кол-во, которое можно купить на заданную сумму, и приводим его к кратному значению
                    my_amount = adjust_to_step(spend_sum, CURR_LIMITS['filters'][2]['stepSize'])
                    print("SELL() my_amount ",my_amount)
                    if my_amount < float(CURR_LIMITS['filters'][2]['stepSize']) or my_amount < float(CURR_LIMITS['filters'][2]['minQty']):
                        print("SELL() Продажа невозможна, выход. Увеличьте размер ставки!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        continue
                    orderID = random.random()

                    print("SELL() Profit is: {profit}; Stop loss is: {sloss}".format(profit=profit,sloss=stloss))
                    return pair_name, orderID, my_amount, spend_sum, profit, stloss, top_price, int(time.time())
        except Exception as e:
            print("Error from SELL()... in AppEmMargin {}".format(e))

    else:
        print("Error from SELL()... init varibale (press button Init)!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

