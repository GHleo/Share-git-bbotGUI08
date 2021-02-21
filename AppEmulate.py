import tkinter as tk
from tkinter import messagebox as msg
from datetime import datetime as dt
import time
import sqlite3
import threading
import configGlb as cnf
import ta
import random
import MarketData
# import requests  # for making http requests to binance
# import json  # for parsing what binance sends back to us
# import pandas as pd  # for storing and manipulating the data we get back
from queriesToDB import (make_initial_tables_emTA, add_new_order_buy_emTA, get_db_open_orders_emTA, update_sell_emTA,make_initial_emTA_ShTr,
                         get_open_orders_emTA_ShTr,add_new_order_buy_emTA_ShTr,update_sell_emTA_ShTr)
import queriesToDB as db

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

#ffffffffffffffffffffffffffff function for Cross MACD alg fffffffffffffffffff
@thread
def e_taTradeMACD(_1th_scrol,_2th_scrol, _3th_scrol, pb00_):
    conn = sqlite3.connect('binance_app08.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    make_initial_tables_emTA(cursor)  # _taTrade
    global isBuing, isSelling
    if not cnf.symbolPairGL:
        msg.showinfo("AppEmulate", 'Please press button -> Init Pairs!')
    print("Получаем все неисполненные ордера по БД fill orders_info!!!")  # SELECT, fill orders_info
    _3th_scrol.insert(tk.END, 'e_taTradeMACD() -> Start!!!' + '\n')
    while cnf.loop_AppEmul < cnf.loopGL and cnf.eml_freezLong_GL:
        try:
            get_db_open_orders_emTA(cursor, cnf.symbolPairGL)
            order_statusB = True
            isBuing, isSelling = True, True
# !!!!!!!!!!!!!!!! BOUGHT need SELL !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            if cnf.orders_infoEm:
                print("Получены неисполненные ордера из БД: {orders}".format(orders=[(order, cnf.orders_infoEm[order]['order_pair']) for order in cnf.orders_infoEm]))
# !!!!!!! snippet SELL Проверяем каждый неисполненный по базе ордер
                delay_ = 0.05
                while isSelling:
                    #print('while isSelling MACD !!!!!!!!!!!!!!!')
                    SordID, FordID, bamount, bprice, sprice, fsprice, balance, order, incomeV,incomeP, profit, stoploss, pairn, currate, bdtSec, isBub = SELL(cnf.orders_infoEm, 'MACD') # -15-
                    #dt_ = dt.strptime(bdt, '%Y-%m-%d %H:%M:%S') #преобразует строку в datetime
                    time_passedM = round((int(time.time()) - bdtSec) / 60, 2)
                    _2th_scrol.delete(0.1, tk.END)
                    _2th_scrol.insert(tk.END, 'sell... MACD isSelling loop; Profit/StopLoss -> ' + str(profit)+ '/' + str(stoploss) + '\n' + 'Bought    -> ' + str(bprice) + '\n'
                                      + 'Curr rate         -> ' + str(currate) + '\n' + 'Aim       -> ' + str(sprice) + '\n' + 'Forc sell -> ' + str(fsprice) + '\n'
                                      + 'Income(%) -> ' + str(incomeP) + '\n' + str(cnf.SELLlng_LIFE_TIME_MIN)+' min. limit; ..... time passed min. ' + str(time_passedM) + '\n')
# !!!!!!!!!!!!!!!!!! Sell MARKET with STOP LOSS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    if cnf.isMRKT_GL:
                        if time_passedM > cnf.SELLlng_LIFE_TIME_MIN and isBub:
                            update_sell_emTA(cursor, conn, SordID, 0, bamount, sprice, 0, balance, order, incomeV,profit) # -11 -
                            _3th_scrol.insert(tk.END, 'Sell... Price-> ' + str(currate) + '; time_passed(min)-> ' + str(time_passedM) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '\nIncome($): ' + str(incomeV) + '\n\n')
                            cnf.loop_AppEmul += 1
                            cnf.eml_freezLong_GL = False
                            break
                        if currate >= sprice:
                            update_sell_emTA(cursor, conn, SordID, 0, bamount, sprice, 0, balance, order, incomeV,profit) # -11 -
                            _3th_scrol.insert(tk.END, 'Sell.. Price-> ' + str(currate) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '\nIncome($): ' + str(incomeV) + '\n\n')
                            isSelling = False  # to proceed at HSTREmulate
                            cnf.eml_freezLong_GL = False
                            break
                        if fsprice > currate and stoploss > 0:
                            update_sell_emTA(cursor, conn, 0, FordID, bamount, 0, fsprice, balance, order, incomeV,profit)
                            _3th_scrol.insert(tk.END, 'Force sell.. Price-> ' + str(fsprice) + '; ' + str(dt.now().strftime('%H:%M:%S')) + str(incomeV) + '\nIncome($)-> ' + '\n\n')
                            cnf.loop_AppEmul += 1
                            cnf.eml_freezLong_GL = False
                            break
# !!!!!!!!!!!!!!!!!! Sell LIMIT with  STOP LOSS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    if cnf.isLMT_GL:
                        if time_passedM > cnf.SELLlng_LIFE_TIME_MIN and isBub:
                            update_sell_emTA(cursor, conn, SordID, 0, bamount, sprice, 0,  balance, order, incomeV,profit) # -11-
                            _3th_scrol.insert(tk.END, 'Sell... Price-> ' + str(sprice) + '; time_passed(min)-> ' + str(time_passedM) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '\nIncome($)-> ' + str(incomeV) + '\n\n')
                            cnf.loop_AppEmul += 1
                            cnf.eml_freezLong_GL = False
                            break
                        if currate >= sprice:
                            update_sell_emTA(cursor, conn, SordID, 0, bamount, sprice, 0,  balance, order, incomeV,profit) # -11-
                            _3th_scrol.insert(tk.END, 'Sell.. Price-> ' + str(sprice) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '\nIncome($)-> ' + str(incomeV)+ '\n\n')
                            cnf.loop_AppEmul += 1
                            cnf.eml_freezLong_GL = False
                            break
                        if fsprice > currate and stoploss > 0:
                            update_sell_emTA(cursor, conn, 0, FordID, bamount, 0, fsprice, balance, order, incomeV,profit) # -11-
                            _3th_scrol.insert(tk.END, 'Force sell.. Price-> ' + str(fsprice) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '\nIncome($) -> ' + str(incomeV) + '\n\n')
                            cnf.loop_AppEmul += 1
                            cnf.eml_freezLong_GL = False
                            break
                    #f not isSelling: break  # Exit from loop isSelling
                    thread = threading.Thread(target=run_progressbar(pb00_, delay_))
                    thread.start()
# !!!!!!!!!!!!!!!! need BUY  Если остались пары, по которым нет текущих торгов
            else:
                while isBuing and cnf.eml_freezLong_GL:
                    cnf.is_taTrade = True  # e_taTradeMACD is working
                    if cnf.orders_infoEm:
                        msg.showinfo("e_taTradeMACD", 'Try Buing, there is -buy- record in ordersEmTa!!! ')
                    # Получаем свечи и берем цены закрытия, high, low
                    klines = cnf.bot.klines(symbol=cnf.symbolPairGL,interval=cnf.KlineGL, limit=cnf.KLINES_LIMITS)
                    klinesMinusLast = klines[:len(klines) - int(cnf.USE_OPEN_CANDLES)]
                    closes = [float(x[4]) for x in klinesMinusLast]
                    cprice = str(cnf.bot.tickerPrice(symbol=cnf.symbolPairGL)['price'])[:7]

                    macd, macdsignal, macdhist = ta.MACD(closes, 7, 14, 9)

                    Ups, Dns = macdSignalCross(macd, macdsignal)# MACD line crosses the signal line Up or Down

                    if not cnf.is_mrgTradeEm:
                         _1th_scrol.delete(0.1, tk.END)
                         _1th_scrol.insert(tk.END, '### Emulating MACD cross Up (e_taTradeMACD) ###' + '\n' + '      (When selling in progress it freez!) ' + '\n\n')
                         _1th_scrol.insert(tk.END, 'MACD -> EMA Short/Long/Signal -> 7/14/9' + '\n\n' + 'KLINES_LIMITS(period)-> ' + str(cnf.KLINES_LIMITS)+ '\n'+ 'TIMEFRAME(in minutes)-> ' + str(cnf.KlineGL) + '\n')
                         _1th_scrol.insert(tk.END, 'Buy  LIFE_TIME_MIN-> '+str(cnf.BUYlng_LIFE_TIME_MIN) + '\n' + 'Sell LIFE_TIME_MIN-> '+str(cnf.SELLlng_LIFE_TIME_MIN) + '\n')
                         _1th_scrol.insert(tk.END, '---------------------------------------------' + '\n\n')
                         _1th_scrol.insert(tk.END, 'Is Market/Limit? -> ' + str(cnf.isMRKT_GL) +'/' + str(cnf.isLMT_GL) + '\n' + 'Is cross Up?     -> ' + str(Ups) + '\n' + 'Rate             -> ' + str(cprice) + '\n')
                         _1th_scrol.insert(tk.END, '---------------------------------------------' + '\n')
# !!!!!!!!!!!!!!!!!! BUY MARKET - MACD - !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    if Ups and cnf.isMRKT_GL: # if MACD cross signal lane OR started from HSTREmulate and Market
                        pname, ordID, myamount, sellLMT, spendsum, profit, stoploss, currate, dtb = BUY('MACD')
                        add_new_order_buy_emTA(cursor, conn, pname, ordID, myamount, currate, spendsum,profit, 0, stoploss) # -10-
                        _3th_scrol.insert(tk.END, 'MACD -MARKET- Pair: ' + str(pname) + '\nBuy.. Price: ' + str(currate) + '; Amount: ' + str(myamount) + '; '+ str(dt.now().strftime('%H:%M:%S')) + '\n')
                        #isBuing = False
                        break # terminate loop -isBuing-
# !!!!!!!!!!!!!!!!!! BUY LIMIT with TIMER - MACD - !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    if Ups and cnf.isLMT_GL:  # if Short trend or started from HSTREmulate and Limit
                        pname, ordID, myamount, sellLMT, spendsum, profit, stoploss, currate, dtb = BUY('MACD')
                        need_priceLMT = round(currate - cnf.nLMTautoDnLng_GL)  # buy low on 10 base crypto ????????? we need correcting sellLMT
                        while order_statusB:
                            curr_rate = round(float(cnf.bot.tickerPrice(symbol=pname)['price']),2)
                            time_passedM = round((int(time.time()) - dtb)/60,2)
                            _2th_scrol.delete(0.1, tk.END)
                            _2th_scrol.insert(0.1,'Buy.. MACD -LIMIT- Current rate -> ' + str(curr_rate) + '\nAim -> ' + str(need_priceLMT) + '\n..... time passed min. ' + str(time_passedM) + '\n')
                            if time_passedM > cnf.BUYlng_LIFE_TIME_MIN: # if time passed Exit from loop -order_statusB-
                                _3th_scrol.insert(tk.END, 'MACD -LIMIT- Pair: ' + str(pname) + '; time_passed min-> ' + str(time_passedM)+ '; cnf.nLMTautoDnLng_GL: ' + str(cnf.nLMTautoDnLng_GL) + ' ****** EXIT ******'+ '\n\n')
                                cnf.eml_freezLong_GL = False
                                isBuing = False
                                break # terminate loop -order_statusB-
                            if curr_rate <= need_priceLMT:
                                add_new_order_buy_emTA(cursor, conn, pname, ordID, myamount, need_priceLMT, spendsum, profit, sellLMT, stoploss) # -10-
                                _3th_scrol.insert(tk.END,'MAKD -LIMIT- Pair: ' + str(pname) + '\nBuy.. Price-> ' + str(currate) + '; Amount: ' + str(myamount)+ '; cnf.nLMTautoDnLng_GL: ' + str(cnf.nLMTautoDnLng_GL) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                isBuing = False
                                print('!!!! e_taTradeMACD... currate: ' + str(currate) + '; cnf.nLMTautoDnLng_GL: ' + str(cnf.nLMTautoDnLng_GL))
                                break
                            time.sleep(5)  # 5sec
                    if not isBuing: break #Exit from loop isBuing
                    thread = threading.Thread(target=run_progressbar(pb00_, cnf.chVarDelay_GL))
                    thread.start()
            cnf.is_taTrade = False  # e_taTradeMACD is not working
            if cnf.loop_AppEmul >= cnf.loopGL:  # Enable loop for HSTR Emulate for cross Up
                _2th_scrol.insert(tk.END, 'e_taTradeMACD TERMINATE! Loop = ' + str(cnf.loop_AppEmul) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                cnf.eml_freezLong_GL = False
        except Exception as e:
            print("ERROR e_taTradeMACD().... from WHILE cnf.loop_AppEmul {}".format(e))
            time.sleep(10)
            continue
    _2th_scrol.insert(tk.END, 'e_taTradeMACD TERMINATE - End Function!  loop_AppEmul = ' + str(cnf.loop_AppEmul) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
    cursor.close()

#ffffffffffffffffffffffffffff function for alg Short Trend fffffffffffffffffff
@thread
def e_taTradeShTrend(_1th_scrol,_2th_scrol, _3th_scrol, pb00_):
    conn2 = sqlite3.connect('binance_app08.db', check_same_thread=False)
    conn2.row_factory = sqlite3.Row
    cursorShTr = conn2.cursor()
    make_initial_emTA_ShTr(cursorShTr)  #
    global isBuing, isSelling
    if not cnf.symbolPairGL:
        msg.showinfo("AppEmulate", 'Please press button -> Init Pairs!')
    print("e_taTradeShTrend... Получаем все неисполненные ордера по БД")  # SELECT, fill orders_info
    get_open_orders_emTA_ShTr(cursorShTr)
    _3th_scrol.insert(tk.END, 'e_taTradeShTr() -> Start!!!' + '\n')
    while cnf.loop_AppEmulShTr < cnf.loopGL and cnf.eml_freezLong_GL:
        try:
            get_open_orders_emTA_ShTr(cursorShTr)
            order_statusB = True
            isSelling, isBuing = True, True
# !!!!!!!!!!!!!!!!!!!!!! BOUGHT need SELL !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            if cnf.orders_infoEmShTr:
                print("Получены неисполненные ордера из БД: {orders}".format(orders=[(order, cnf.orders_infoEmShTr[order]['order_pair']) for order in cnf.orders_infoEmShTr]))
                delay_ = 0.05
                while isSelling:
                    SordID, FordID, bamount, bprice, sprice, fsprice, balance, order, incomeV,incomeP, profit, stoploss, pairn, currate, bdtSec, isBub= SELL(cnf.orders_infoEmShTr,'ShortTrend') # -15-
                    time_passedM = round((int(time.time()) - bdtSec) / 60, 2)
                    _2th_scrol.delete(0.1, tk.END)
                    _2th_scrol.insert(tk.END, 'Sell... Short Trend; Profit/StopLoss -> ' + str(profit)+ '/' + str(stoploss) + '\n' + 'Bought    -> ' + str(bprice) + '\n'
                                      + 'Curr rate ->        ' + str(currate) + '\n' + 'Aim       -> ' + str(sprice) + '\n' + 'Forc sell -> ' + str(fsprice) + '\n'
                                      + 'Income(%) -> ' + str(incomeP) + '\n' + '..... time passed min. ' + str(time_passedM) + '\n')
# !!!!!!!!!!!!!! Sell MARKET WITH STOP LOSS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    if cnf.isMRKT_GL:
                        if time_passedM > cnf.SELLlng_LIFE_TIME_MIN and isBub:
                            update_sell_emTA_ShTr(cursorShTr, conn2, SordID, 0, bamount, sprice, 0, balance, order, incomeV, profit)
                            _3th_scrol.insert(tk.END, 'SellBUB... Price-> ' + str(currate) + '; time_passed-> ' + str(time_passedM) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '\nIncome($) -> ' + str(incomeV) + '\n\n')
                            cnf.loop_AppEmulShTr += 1
                            cnf.eml_freezLong_GL = False
                            break
                        if currate > sprice:
                            update_sell_emTA_ShTr(cursorShTr, conn2, SordID, 0, bamount, sprice, 0, balance, order, incomeV, profit)
                            _3th_scrol.insert(tk.END, 'Sell... Price-> ' + str(currate) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '\nIncome($) -> ' + str(incomeV) + '\n\n')
                            cnf.loop_AppEmulShTr += 1
                            cnf.eml_freezLong_GL = False
                            break
                        if fsprice > currate and stoploss > 0:
                            update_sell_emTA_ShTr(cursorShTr, conn2, 0, FordID, bamount, 0, fsprice, balance, order, incomeV, profit)
                            _3th_scrol.insert(tk.END, 'Force sell... Price-> ' + str(fsprice)+ '; ' + str(dt.now().strftime('%H:%M:%S')) + '\nIncome($) -> ' + str(incomeV) + '\n\n')
                            cnf.loop_AppEmulShTr += 1
                            cnf.eml_freezLong_GL = False
                            break
# !!!!!!!!!!!!!! Sell LIMIT WITH STOP LOSS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    if cnf.isLMT_GL:
                       if time_passedM > cnf.SELLlng_LIFE_TIME_MIN and isBub:
                           update_sell_emTA_ShTr(cursorShTr, conn2, SordID, 0, bamount, sprice, 0, balance, order,incomeV, profit)
                           _3th_scrol.insert(tk.END, 'Sell... Price-> ' + str(sprice) + '; time_passed(min)-> ' + str(time_passedM) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '\nIncome($) -> ' + str(incomeV) + '\n\n')
                           cnf.loop_AppEmulShTr += 1
                           cnf.eml_freezLong_GL = False
                           break
                       if currate >= sprice:
                          update_sell_emTA_ShTr(cursorShTr, conn2, SordID, 0, bamount, sprice, 0, balance, order, incomeV, profit)
                          _3th_scrol.insert(tk.END, 'Sell.. Price-> ' + str(sprice) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '\nIncome($)-> ' + str(incomeV) + '\n\n')
                          cnf.loop_AppEmulShTr += 1
                          cnf.eml_freezLong_GL = False
                          break
                       if fsprice > currate and stoploss > 0:
                           update_sell_emTA_ShTr(cursorShTr, conn2, 0, FordID, bamount, 0, fsprice, balance, order, incomeV, profit)
                           _3th_scrol.insert(tk.END, 'Force Sell.. Price-> ' + str(fsprice) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '\nIncome($)-> ' + str(incomeV) + '\n\n')
                           cnf.loop_AppEmulShTr += 1
                           cnf.eml_freezLong_GL = False
                           break

                    thread = threading.Thread(target=run_progressbar(pb00_, delay_))
                    thread.start()
# !!!!!!!!!!!!!!!!!!!!!!!!!!! need BUY  Если остались пары, по которым нет текущих торгов !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            else:
                cnf.is_taTrade = True  # e_taTradeShTrend is working now
                while isBuing and cnf.eml_freezLong_GL:
                     # Получаем свечи и берем цены закрытия, high, low
                     klines = cnf.bot.klines(symbol=cnf.symbolPairGL,interval=cnf.KlineGL,limit=cnf.KLINES_LIMITS)
                     klinesMinusLast = klines[:len(klines) - int(cnf.USE_OPEN_CANDLES)]
                     opens = [float(x[1]) for x in klinesMinusLast]
                     closes = [float(x[4]) for x in klinesMinusLast]
                     cprice = str(cnf.bot.tickerPrice(symbol=cnf.symbolPairGL)['price'])[:7]
                     isUp, isBigUp, isDn, isBigDn = ta.ShortTrend(closes[-int(cnf.fastMoveCount):],opens[-int(cnf.fastMoveCount):])
                     if not cnf.is_mrgTradeEm: # one scrool for two algo - if work margin this take off
                         _1th_scrol.delete(0.1, tk.END)
                         _1th_scrol.insert(tk.END,'### Emulating Short Trend (e_taTradeShTrend) ###' + '\n' + '      (When selling in progress it freez!) ' + '\n\n')
                         _1th_scrol.insert(tk.END, 'KLINES_LIMITS(period)-> ' + str(cnf.KLINES_LIMITS) + '\n' + 'TIMEFRAME(in minutes)-> ' + str(cnf.KlineGL) + '\n')
                         _1th_scrol.insert(tk.END, 'Buy  LIFE_TIME_MIN-> ' + str(cnf.BUYlng_LIFE_TIME_MIN) + '\n' + 'Sell LIFE_TIME_MIN-> ' + str(cnf.SELLlng_LIFE_TIME_MIN) + '\n')
                         _1th_scrol.insert(tk.END, '---------------------------------------------' + '\n\n')
                         _1th_scrol.insert(tk.END, 'Is Market/Limit? -> ' + str(cnf.isMRKT_GL) + '/' + str(cnf.isLMT_GL) + '\n' + 'Is 3 candles Grow/Down? -> ' + str(isUp) + '/' + str(isDn) + '\n' + 'Rate                    -> ' + str(cprice) + '\n')
                         _1th_scrol.insert(tk.END, 'Is last candle Grow/Down? -> ' + str(isBigUp) + '/' + str(isBigDn) + '\n' +'---------------------------------------------' + '\n')

# !!!!!!!!!!!!!!!!!! BUY MARKET !!!!!!!!!!!!!! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!sell(limit)... curr_rate
                     if (isDn or isBigDn) and cnf.isMRKT_GL:  # if SHORT TREND or STARTED from HSTREmulate and Market
                         pname, ordID, myamount, needprice, spendsum, profit, stoploss, currate, dtb = BUY('ShortTrend')
                         add_new_order_buy_emTA_ShTr(cursorShTr, conn2, pname, ordID, myamount, currate, spendsum, profit, stoploss,0)
                         _3th_scrol.insert(tk.END, 'Buy... ShortTrend -MARKET- Pair: ' + str(pname) + '\nPrice: ' + str(currate) + '; Amount: ' + str(myamount) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                         #isBuing = False
                         break  # terminate loop -isBuing-
# !!!!!!!!!!!!!!!!!! BUY LIMIT with TIMER !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                     if (isDn or isBigDn) and cnf.isLMT_GL:  # if Short trend or started from HSTREmulate and Limit
                         pname, ordID, myamount, sellLMT, spendsum, profit, stoploss, currate, dtb = BUY('ShortTrend')
                         need_priceLMT = round(currate - cnf.nLMTautoDnLng_GL,2) # buy low on 10 base crypto ????????? we need correcting sellLMT
                         while order_statusB:
                             curr_rate = round(float(cnf.bot.tickerPrice(symbol=cnf.symbolPairGL)['price']),2)
                             time_passedM = round(int(time.time() - dtb)/60,2)
                             _2th_scrol.delete(0.1, tk.END)
                             _2th_scrol.insert(tk.END, 'buy ShortTrend -LIMIT- Cur rate-> ' + str(curr_rate ) + '; Aim-> ' + str(need_priceLMT) + '\n..... time passed min. ' + str(time_passedM) + '\n')
                             if time_passedM > cnf.BUYlng_LIFE_TIME_MIN:
                                 _3th_scrol.insert(tk.END, 'Buy... ShortTrend -LIMIT- Pair: ' + str(pname) + '; time_passed min-> '+ str(time_passedM)+ '; cnf.nLMTautoDnLng_GL: ' + str(cnf.nLMTautoDnLng_GL)+ '; ' + ' ****** EXIT ******' + '\n')
                                 cnf.eml_freezLong_GL = False  # Exit from function
                                 isBuing = False
                                 break # terminate loop -order_statusB-
                             if curr_rate <= need_priceLMT: # if limit
                                add_new_order_buy_emTA_ShTr(cursorShTr, conn2, pname, ordID, myamount, need_priceLMT, spendsum, profit,stoploss, sellLMT)
                                _3th_scrol.insert(tk.END, 'Buy... ShortTrend -LIMIT- Pair: ' + str(pname) + '\nPrice: ' + str(currate) + '; Amount: ' + str(myamount) + '; cnf.nLMTautoDnLng_GL: ' + str(cnf.nLMTautoDnLng_GL)+ '; ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                print('!!!! e_taTradeShTrend()... currate: ' + str(currate) + '; cnf.nLMTautoDnLng_GL: ' + str(cnf.nLMTautoDnLng_GL))
                                isBuing = False
                                break #Exit from loop isBuing
                             time.sleep(5) #5sec
                     if not isBuing: break #Exit from loop order_isBuing
                     thread = threading.Thread(target=run_progressbar(pb00_, cnf.chVarDelay_GL))
                     thread.start()
            cnf.is_taTrade = False  # e_taTradeShTrend is not working
            if cnf.loop_AppEmulShTr >= cnf.loopGL:  # Enable loop for HSTR Emulate for cross Up
                _2th_scrol.insert(tk.END, 'e_taTradeShTrend TERMINATE! Loop = ' + str(cnf.loop_AppEmulShTr) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                cnf.eml_freezLong_GL = False
        except Exception as e:
            print("ERROR e_taTradeShTrend().... from WHILE cnf.loop_AppEmulShTr {}".format(e))
            time.sleep(10)
            continue
    _2th_scrol.insert(tk.END, 'e_taTradeShTrend TERMINATE - End Function!  loop_AppEmulShTr = ' + str(cnf.loop_AppEmulShTr) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
    cursorShTr.close()

def BUY(algorithm):
    try:
        # Если остались пары, по которым нет текущих торгов
        if cnf.pairsGL:
            for pair_name, pair_obj in cnf.pairsGL.items():
                #profit = pair_obj['profit_markup']
                profit = cnf.profitEm
                stloss = pair_obj['stop_loss']
                print("Работаем с парой {pair}".format(pair=pair_name))
                for elem in limits['symbols']:
                    if elem['symbol'] == pair_name:
                        CURR_LIMITS = elem
                        break
                else:
                    raise Exception("BUY()... Не удалось найти настройки выбранной пары " + pair_name)
                curr_rate = float(cnf.bot.tickerPrice(symbol=pair_name)['price'])
                # Среднюю цену приводим к требованиям биржи о кратности
                my_need_price = adjust_to_step(curr_rate, CURR_LIMITS['filters'][0]['tickSize'])
                sellLMT = round(my_need_price * (1 + profit/100 + 0.0015),4)#!!!!!!!!!! temp value for limit sell
                spend_sum = pair_obj['spend_sum']
                # Рассчитываем кол-во, которое можно купить, и тоже приводим его к кратному значению
                my_amount = adjust_to_step(spend_sum / my_need_price, CURR_LIMITS['filters'][2]['stepSize'])
                orderID = random.randrange(1000000, 1999999)

                print("BUY() Profit is: {profit}; Stop loss is: {sloss}".format(profit=profit, sloss=stloss))
                return pair_name, orderID, my_amount, sellLMT, spend_sum, profit, stloss, curr_rate, int(time.time())
        else:
            print("Error from BUY()... init varibale (press button Init)!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    except Exception as e:
        print("Error from BUY()... in AppEmulate {}".format(e))

def SELL(orders_info,s_algorithm):
    try:
       isBub = False
       for order, value in orders_info.items():
          # profit_markup = round(cnf.pairsGL[value['order_pair']]['profit_markup'], 4)
           profit_markup = cnf.profitEm
           stloss = value['panic_fee']
           # смотрим, какие ограничения есть для создания ордера на продажу
           for elem in limits['symbols']:
               if elem['symbol'] == value['order_pair']:
                   CURR_LIMITS = elem
                   break
           else:
               raise Exception("Не удалось найти настройки выбранной пары " + 'limit')

           if value['panic_fee'] > 0:
               fsell_price = round(value['buy_price'] * (100 - value['panic_fee']-0.15) / 100,4)
           else:
               fsell_price = 0

           # Рассчитываем минимальную сумму, которую нужно получить, что бы остаться в плюсе ЗА ВЫЧЕТОМ ПРОЦЕНТА c BNB
           sell = value['buy_price'] * (1 + value['profit'] / 100 + 0.0015)
           sell_price = adjust_to_step(sell, CURR_LIMITS['filters'][0]['tickSize'])
           curr_rate = float(cnf.bot.tickerPrice(symbol=value['order_pair'])['price'])

           ForderID = random.randrange(1000000, 1999999)
           SorderID = random.randrange(1000000, 1999999)

           incomeV = round(value['buy_amount'] * curr_rate * (1 - 0.00075) - (value['buy_amount'] * value['buy_price']) * (1 - 0.00075),2)
           incomeP = round((curr_rate / value['buy_price'] - 1)* 100, 2)

           bub = value['buy_price'] * (1 + 0.0015)
           if curr_rate > bub:
               isBub = True
           buyDate = dt.strptime(value['buy_created'],'%Y-%m-%d %H:%M:%S')  # преобразует строку в datetime; timestamp() - возвращает время в секундах с начала эпохи.
           buyDateSec = buyDate.timestamp()

           return SorderID, ForderID,value['buy_amount'], value['buy_price'], sell_price, fsell_price,value['balance'],order,incomeV,incomeP,profit_markup,stloss,value['order_pair'],curr_rate, buyDateSec, isBub
    except Exception as e:
        print("Error from SELL()... in AppEmulate {}".format(e))

def getInfo(a1th_scrol,a2th_scrol,a3th_scrol):
    md = MarketData.MarketData()
    conn = sqlite3.connect('binance_app08.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    a1th_scrol.delete(0.1, tk.END)
    a2th_scrol.delete(0.1, tk.END)
    a3th_scrol.delete(0.1, tk.END)

    db.get_open_orders_appTA(cursor) #get open orders in table -ordersTA-, fill cnf.orders_infoMACD
    db.get_open_orders_appTA_ShTr(cursor)  # get open orders in table -ordersTAShTr-, fill cnf.orders_infoShTr
    db.get_open_orders_MRG(cursor) # get open orders in table -ordersMrg-, cnf.orders_infoMrgMACD
    db.get_open_orders_MRG_ShTr(cursor) # get open orders in table -ordersMrgShTr-, cnf.orders_infoMrgShTr

    klines24h = cnf.client.get_klines(symbol=cnf.symbolPairGL, interval='6h', limit=4)
    klines4h = cnf.client.get_klines(symbol=cnf.symbolPairGL, interval='1h', limit=4)
    closes24h = [float(x[4]) for x in klines24h]
    volume24 = [float(x[5]) for x in klines24h]
    volumeQ24 = [float(x[7]) for x in klines24h]
    closes4h = [float(x[4]) for x in klines4h]
    volume4 = [float(x[5]) for x in klines4h]
    mtmPrd24, mtmPrd4 = md.MTM() #return 24h, 12h, 6h, 4h, 2h, 1h

    klines = cnf.client.get_klines(symbol=cnf.symbolPairGL, interval=cnf.KlineGL, limit=cnf.KLINES_LIMITS)
    klinesMinusLast = klines[:len(klines) - int(cnf.USE_OPEN_CANDLES)]
    closes = [float(x[4]) for x in klinesMinusLast]
    opens = [float(x[1]) for x in klinesMinusLast]
    high = [float(x[2]) for x in klinesMinusLast]
    low = [float(x[3]) for x in klinesMinusLast]
    closes_time = [float(x[6]) for x in klinesMinusLast]
    dt_ = [dt.fromtimestamp(round(x / 1000)) for x in closes_time]
    dt_HM = [dt.strftime(x,'%H:%M') for x in dt_]

    klinesMrg = cnf.client.get_klines(symbol=cnf.symbolPairGL, interval=cnf.KlineMrgGL, limit=cnf.KLINES_LIMITS)
    klinesMinusLastMrg = klinesMrg[:len(klinesMrg) - int(cnf.USE_OPEN_CANDLES)]
    closesMrg = [float(x[4]) for x in klinesMinusLastMrg]
    opensMrg = [float(x[1]) for x in klinesMinusLastMrg]
    highMrg = [float(x[2]) for x in klinesMinusLastMrg]
    lowMrg = [float(x[3]) for x in klinesMinusLastMrg]
    closes_timeMrg = [float(x[6]) for x in klinesMinusLastMrg]
    dt_Mrg = [dt.fromtimestamp(round(x / 1000)) for x in closes_timeMrg]
    dt_HM_Mrg = [dt.strftime(x,'%H:%M') for x in dt_Mrg]

    price = round(float(cnf.client.get_symbol_ticker(symbol=cnf.symbolPairGL)['price']),2)
    print('volume24: ' + str(sum(volume24)))
    print('volumeQ24: ' + str(sum(volumeQ24)))
    #l3Up, bUp = round(float(price) * cnf.Up3LastSet/100,2), round(float(price) * cnf.bigUpPercent/100,2)
    #l3Dn, bDn = round(float(price) * cnf.Dn3LastSet/100,2), round(float(price) * cnf.bigDnPercent/100,2)
    lUp, _lstBodyDnLng, mxUp,maxBody_DnLng, bodyCndl10Lng = ta.Extremums(high, low, closes, opens,dt_HM) #time frame for Long
    _lstBodyUpMrg, lDn, _maxBody_UpMrg,mDn, bodyCndl10Mrg = ta.Extremums(highMrg, lowMrg, closesMrg, opensMrg,dt_HM_Mrg) #time frame Margin

    isUp, isBigUp, isDn, isBigDn = ta.ShortTrend(closes[-int(cnf.fastMoveCount):], opens[-int(cnf.fastMoveCount):])

    lstUp01, lstUp02, lstUp03, lstDn01, lstDn02, lstDn03, max_indexUpMrg, rcmUpMrg, max_indexDnLng, rcmDnLng = listCndlMinPercents(_lstBodyUpMrg, _lstBodyDnLng)
    #listMin01Mrg, listMin02Mrg, listMin03Mrg, listMin01DnMrg, listMin02DnMrg, listMin03DnMrg, _max_indexUpMrg, rec, max_indexDnMrg, recomendMrgVal = listCndlMinPercents(_lstBodyUpMrg, lstBodyDn) # for Margin

    CalcProfit = listHL_MinPercents(high,low,dt_HM, lUp, _lstBodyDnLng, price)
    #print('getInfo() cnf.KlineGL: ' + str(cnf.KlineGL) + '\nmaxBody_Up: ' + str(maxBody_Up)+ '\nmaxBody_Dn: ' + str(maxBody_Dn))
    #print('getInfo() cnf.KlineMrgGL: ' + str(cnf.KlineMrgGL) + '\nmaxBody_UpMrg: ' + str(maxBody_UpMrg)+ '\nmaxBody_DnMrg: ' + str(maxBody_DnMrg))
    maxBodyUpMrg, maxBodyDnLng = '',''
    if max_indexUpMrg == 0: maxBodyUpMrg = '(Max body - 0.1%)'
    if max_indexUpMrg == 1: maxBodyUpMrg = '(Max body - 0.2%)'
    if max_indexUpMrg == 2: maxBodyUpMrg = '(Max body - 0.3%)'

    if max_indexDnLng == 0: maxBodyDnLng = '(Max body - 0.1%)'
    if max_indexDnLng == 1: maxBodyDnLng = '(Max body - 0.2%)'
    if max_indexDnLng == 2: maxBodyDnLng = '(Max body - 0.3%)'

    Last10LngAvr = round(sum(bodyCndl10Lng)/len(bodyCndl10Lng),4)
    #cnf.bigUpPercent = C_Last10Avr
    Last10MrgAvr = round(sum(bodyCndl10Mrg)/len(bodyCndl10Mrg),4)

    a1th_scrol.insert(tk.END, 'PERIOD, Limit(count) candles-> ' + str(cnf.KLINES_LIMITS) + '\n\n')
    a1th_scrol.insert(tk.END, 'LONG. Time frame: ' + str(cnf.KlineGL) + '\nLast 10 body candles: ' + str(bodyCndl10Lng) + '\nAverage. Recommended for -Delta for Limits($)- ' + str(Last10LngAvr) + '\n')
    a1th_scrol.insert(tk.END, 'MARGIN. Time frame: ' + str(cnf.KlineMrgGL) + '\nLast 10 body candles: ' + str(bodyCndl10Mrg) + '\nAverage. Recommended for -Delta for Limits($)- ' + str(Last10MrgAvr) + '\n\n')
    a1th_scrol.insert(tk.END, 'Momentums; Volumes: \nPeriod 24h: ' + str(mtmPrd24[0]) + '; Vol: ' + str(sum(volume24))+ '\nPeriod 12h: ' + str(mtmPrd24[1])+ '; Vol: ' + str(volume24[2]+volume24[3]) + '\nLast    6h: ' + str(mtmPrd24[2])+ '; Vol: ' + str(volume24[3]) + '\n')
    a1th_scrol.insert(tk.END, 'Period 4h: ' + str(mtmPrd4[0]) + '; Vol: ' + str(volume4[0])+ '\nPeriod 2h: ' + str(mtmPrd4[1]) + '; Vol: ' + str(volume4[1]) + '\nLast   1h: ' + str(mtmPrd4[2])+ '; Vol: ' + str(volume4[2]))
    a1th_scrol.insert(tk.END, '\n\nRecomend for Profit (High(-0.2%) - Low(-0.2%)/CPrice: ' + str(CalcProfit) + '%')

    a2th_scrol.insert(tk.END, '------ LONG ------ \n')
    a2th_scrol.insert(tk.END, 'Max body for PERIOD, get Down -> ' + str(round(maxBody_DnLng[2],2)) +'%/'+ str(maxBody_DnLng[1]) + '$' + '\n(Max body - 0.1%)->' + str(lstDn01) + '\n(Max body - 0.2%)->' + str(lstDn02) + '\n(Max body - 0.3%)->' + str(lstDn03)+ '\n')
    a2th_scrol.insert(tk.END, 'Recommended For Long:\n' + str(maxBodyDnLng) + '; bigDnPercent-> ' + str(rcmDnLng) + '\n\n')

    a2th_scrol.insert(tk.END, '------ SHORT ------ \n')
    a2th_scrol.insert(tk.END, 'Max body for PERIOD,   get Up -> ' + str(round(_maxBody_UpMrg[2],2)) +'%/'+ str(_maxBody_UpMrg[1]) + '$' + '\n(Max body - 0.1%)->' + str(lstUp01) + '\n(Max body - 0.2%)->' + str(lstUp02) + '\n(Max body - 0.3%)->' + str(lstUp01)+ '\n')
    a2th_scrol.insert(tk.END, 'Recommended For Margin:\n' + str(maxBodyUpMrg) + '; bigUpPercent-> ' + str(rcmUpMrg) + '\n\n')

    a2th_scrol.insert(tk.END, 'Open orders in tables: \nLong ShortTrend (ordersTAShTr): ' + str(cnf.orders_infoShTr) + '\nMargin ShortTrend (ordersMrgShTr): ' + str(cnf.orders_infoMrgShTr) + '\n\n')
    a3th_scrol.insert(tk.END,'Open orders in tables: \nLong taTrade (ordersTA): ' + str(cnf.orders_infoMACD) + '\nMargin taTrade (ordersMrg): ' + str(cnf.orders_infoMrgMACD) + '\n\n')
    a3th_scrol.insert(tk.END,'Changes in percent. \nCurrent rate: ' + str(price) + '\n0.2% -> ' + str(round(price*0.002,2)) + '\n0.4% -> ' + str(round(price*0.004,2)) + '\n0.6% -> ' + str(round(price*0.006,2)) + '\n0.8% -> ' + str(round(price*0.008,2))
                      + '\n1% -> ' + str(round(price*0.01,2)) + '\n2% -> ' + str(round(price*0.02,2)) + '\n3% -> ' + str(round(price*0.03,2))+ '\n\n')

    md.printTest()
    cursor.close()

    return rcmUpMrg, rcmDnLng, Last10LngAvr, Last10MrgAvr, CalcProfit


def e_select4Tables(hours,countTrades,prntLimit):
    # hours - time frame for select; countTrades -  how many positive trades in sequence
    conn = sqlite3.connect('binance_app08.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    valueNeg = [0,0,0,0]
    valuePos = [0,0,0,0]
    cnf.sum_eNegTrades_Gl[1] = 0
    cnf.sum_ePosTrades_Gl[1] = 0
    isTradesPos = False # if there are positive trades in the sequence, and there is none negative

    ordersEmTA,ordersEmMrg,ordersEmTAShTr,ordersEmMrgShTr = db.get_rec_4TablesEm(cursor,hours)

    for item in ordersEmTA: # Select negative income in ordersTA table
        if item[11] < 0:
            valueNeg[0] += 1
            cnf.sum_eNegTrades_Gl[1] += item[11] # sum negative values
        else:
            valuePos[0] += 1
            cnf.sum_ePosTrades_Gl[1] += item[11] # sum negative values

    for item in ordersEmMrg: # Select negative income in ordersMrg table
        if item[13] < 0:
            valueNeg[1] += 1
            cnf.sum_eNegTrades_Gl[1] += item[13] # sum negative values
        else:
            valuePos[1] += 1
            cnf.sum_ePosTrades_Gl[1] += item[13] # sum negative values

    for item in ordersEmTAShTr: # Select negative income in ordersTAShTr table
        if item[11] < 0:
            valueNeg[2] += 1
            cnf.sum_eNegTrades_Gl[1] += item[11] # sum negative values
        else:
            valuePos[2] += 1
            cnf.sum_ePosTrades_Gl[1] += item[11] # sum negative values

    for item in ordersEmMrgShTr:# Select negative income in ordersMrgShTr table
        if item[13] < 0:
            valueNeg[3] += 1
            cnf.sum_eNegTrades_Gl[1] += item[13] # sum negative values
        else:
            valuePos[3] += 1
            cnf.sum_ePosTrades_Gl[1] += item[13] # sum negative values

    cnf.sum_eNegTrades_Gl[0] = round(sum([v for v in valueNeg]),2) # for sum items
    cnf.sum_ePosTrades_Gl[0] = round(sum([v for v in valuePos]),2) # for sum items
    cntTotal = cnf.sum_eNegTrades_Gl[0] + cnf.sum_ePosTrades_Gl[0]
    prntNeg = 0
    if cntTotal > 0:
        prntNeg = round((cntTotal - cnf.sum_ePosTrades_Gl[0])/cntTotal * 100,2) # Percent negative trades at all trades(cntTotal)
    isTradesPosAll = True if (prntNeg <= prntLimit) and (cntTotal >= 4) else False # TRUE if count negative trades <= set percent (for example 75%)
    #print('e_select4Tables()... cntTotal-> '+str(cntTotal) + '; prntNeg-> '+str(prntNeg)+ '; isTradesPosAll-> '+str(isTradesPosAll))

    if cnf.sum_eNegTrades_Gl[0] == 0 and cnf.sum_ePosTrades_Gl[0] >= countTrades:
        isTradesPos = True

    cursor.close()
    return isTradesPos, isTradesPosAll, prntNeg

# func обрезает список свечей на рост(lstBodyUp) падение(lstBodyDn) на 0.1, 0.2, 0.3 % соответсвенно
def listCndlMinPercents(lstBodyUp, lstBodyDn): # lstBodyUp - for Margin; lstBodyDn - for Long
    BodyUpIndex,avrUpValue,BodyDnIndex,avrDnValue= [0,0,0],[0,0,0],[0,0,0],[0,0,0] #[0-Weight(3 or 0 for 0.1), 1-Weight(2 or 0 for 0.2), 2-Weight(1 max for 0.3)],[0 - count of -0.1, 1 - count of -0.2, 2 - count of -0.3]
    maxBodyUp = max(lstBodyUp, key=lambda x: x[1]) #select by index 1 (cost)
    maxBodyDn = max(lstBodyDn, key=lambda x: x[1])
    #print('listCndlMinPercentss()... \nlstBodyUp:' + str(lstBodyUp) + '\nmaxBodyUp: ' + str(maxBodyUp) + '\nmaxBodyDn: ' + str(maxBodyDn))
    lstUp01,lstUp02,lstUp03 = [],[],[] # lists Up - 0.1, -0.2, -0.3 for Margin
    lstDn01,lstDn02,lstDn03 = [],[],[] # lists Down - 0.1, -0.2, -0.3 for Long
    for b in lstBodyUp: #for Margin
        if (maxBodyUp[2] - 0.1) <= b[2]:  # -0.1% from max
            lstUp01.append(round(b[2],2)) 
        if (maxBodyUp[2] - 0.2) <= b[2]:  # -0.2% from max
            lstUp02.append(round(b[2],2)) 
        if (maxBodyUp[2] - 0.3) <= b[2]:  # -0.3% from max
            lstUp03.append(round(b[2],2)) 
            
    for b in lstBodyDn: #for Long
        if maxBodyDn[2] - 0.1 <= b[2]:  # -0.1% from max
            lstDn01.append(round(b[2],2))
        if maxBodyDn[2] - 0.2 <= b[2]:  # -0.2% from max
            lstDn02.append(round(b[2],2))
        if maxBodyDn[2] - 0.3 <= b[2]:  # -0.3% from max
            lstDn03.append(round(b[2],2))

    #print('lstUp01: ' + str(lstUp01) + '; lstUp02: ' + str(lstUp02) + '; lstUp03: ' + str(lstUp03))
    #print('lstDn01: ' + str(lstDn01) + '; lstDn02: ' + str(lstDn02) + '; lstDn03: ' + str(lstDn03))

    if len(lstUp01) >= 3: #if more value in list highest priority
        BodyUpIndex[0] = 3 # 3 высший приоритет из 1,2 и 3
        avrUpValue[0] = round(sum(lstUp01)/len(lstUp01),4)
    if len(lstUp02) >= 3: #if more value in list midle priority
        BodyUpIndex[1] = 2
        avrUpValue[1] = round(sum(lstUp02)/len(lstUp02),4)
    if len(lstUp03) >= 3: #if more value in list less priority
        BodyUpIndex[2] = 1
        avrUpValue[2] = round(sum(lstUp03)/len(lstUp03),4)

    if len(lstDn01) >= 3: #if more value in list highest priority
        BodyDnIndex[0] = 3 #highest priority for list -0.1
        avrDnValue[0] = round(sum(lstDn01)/len(lstDn01),4)
    if len(lstDn02) >= 3: #if more value in list midle priority
        BodyDnIndex[1] = 2
        avrDnValue[1] = round(sum(lstDn02)/len(lstDn02),4)
    if len(lstDn03) >= 3: #if more value in list less priority
        BodyDnIndex[2] = 1
        avrDnValue[2] = round(sum(lstDn03)/len(lstDn03),4)

    max_indexUpMrg = avrUpValue.index(max(avrUpValue)) # get max index [0 = 3 (Max body - 0.1%), 1 = 2 (Max body - 0.2%), 2 = 1 (Max body - 0.3%)]
    #print('avrUpValue: ' + str(avrUpValue))
    #print('max_indexUpMrg: ' + str(max_indexUpMrg))
    if max_indexUpMrg == 0: #if values are less than 3 если все нулевые значения
        rcmUpMrg = round(maxBodyUp[2]/2,4)
    else:
        rcmUpMrg = avrUpValue[max_indexUpMrg]
        #print('recomend Up(Mrg): ' + str(rcmUpMrg))

    max_indexDnLng = avrDnValue.index(max(avrDnValue)) # get max index [0 = 3 (Max body - 0.1%), 1 = 2 (Max body - 0.2%), 2 = 1 (Max body - 0.3%)]
    if max_indexDnLng == 0: #if values are less than 3
        rcmDnLng = round(maxBodyDn[2]/2,4)
    else:
        rcmDnLng = avrDnValue[max_indexDnLng]
        #print('recomend Dn(Lng): ' + str(rcmDnLng))


    #print('listCndlMinPercentss()... \nlist body Up:' + str(lstBodyUp) + '\nmaxBodyUp: ' + str(maxBodyUp)+ '\n(maxBodyUp - 0.1): ' + str(maxBodyUp[2] - 0.1)+ '\nLists:\n-0.1: ' + str(lstUp01) + '\n-0.2: ' + str(lstUp02)+ '\n-0.3: ' + str(lstUp03)+ '\nrecomend Up Mrg: ' + str(rcmUpMrg)+'\n\n')
    #print('listCndlMinPercentss()... \nlist body Dn:' + str(lstBodyDn) + '\nmaxBodyDn: ' + str(maxBodyDn)+ '\n(maxBodyDn - 0.1): ' + str(maxBodyDn[2] - 0.1)+ '\nLists:\n-0.1: ' + str(lstDn01) + '\n-0.2: ' + str(lstDn02)+ '\n-0.3: ' + str(lstDn03)+ '\nrecomend Dn Lng: ' + str(rcmDnLng))

    return lstUp01,lstUp02,lstUp03,lstDn01,lstDn02,lstDn03, max_indexUpMrg, rcmUpMrg, max_indexDnLng, rcmDnLng

def listHL_MinPercents(H,L,dt_, lstBodyUp, lstBodyDn, price):

    H_01,H_01Avr, H_02, H_02Avr,L_01,L_01Avr,L_02,L_02Avr, = [],[],[],[],[],[],[],[]
    mH,mxBodyUp,mxBodyDn = max(H),max(lstBodyUp, key=lambda x: x[1]),max(lstBodyDn, key=lambda x: x[1])
    mL = min(L)
    H01 = mH * (1 - 0.01) # High - 1%
    H02 = mH * (1 - 0.02) # High - 1%
    L01 = mL * (1 + 0.01) # High - 1%
    L02 = mL * (1 + 0.02) # High - 1%

    i01,i02,l01,l02 = 0,0,0,0
    for h,l,dtt in zip(H,L,dt_):
        if H01 <= h:  # -1% from max
            H_01.append([h,dtt])
            i01+=1
        if H02 <= h:  # -2% from max
            H_02.append([h, dtt])
            i02 += 1
        if L01 >= l:  # -1% from max
            L_01.append([l, dtt])
            l01 += 1
        if L02 >= l:  # -2% from max
            L_02.append([l, dtt])
            l02 += 1
    print('H_01: ' + str(len(H_01)))
    H_01Avr = round(sum(i01[0] for i01 in H_01)/len(H_01),2)
    H_02Avr = round(sum(i02[0] for i02 in H_02)/len(H_02),2)
    L_01Avr = round(sum(i01[0] for i01 in L_01)/len(L_01),2)
    L_02Avr = round(sum(i02[0] for i02 in L_02)/len(L_02),2)

    print('listHL_MinPercents(). List High: ' + str(H) + '\nmax High:      ' + str(mH)+ '\nmax High - 1%: ' + str(H01)+ '\nAvr High - 1%: ' + str(H_01Avr)+ '\nAvr High - 2%: ' + str(H_02Avr)+ '\n- 1% count: ' + str(i01)+ '\n- 2% count: ' + str(i02))
    print('listHL_MinPercents(). List Low:  ' + str(L) + '\nmax  Low:      ' + str(mL)+ '\nmax  Low - 1%: ' + str(L01)+ '\nAvr Low  - 1%: ' + str(L_01Avr)+ '\nAvr Low  - 2%: ' + str(L_02Avr)+ '\n- 1% count: ' + str(l01)+ '\n- 2% count: ' + str(l02))
    print('listHL_MinPercents(). Delta (max High - max  Low): ' + str(mH-mL) + '\nDelta (max High - 1%) - (max  Low - 1%):  ' + str(H_01Avr - L_01Avr)+ '\nDelta (max High - 2%) - (max  Low - 2%):  ' + str(H_02Avr - L_02Avr))

    print('max bodyUp: ' + str(mxBodyUp) + '\nmax bodyDn: ' + str(mxBodyDn))
    print('(price - H_01Avr): ' + str(price - H_01Avr) + '\n(price - L_01Avr): ' + str(price - L_01Avr))
    HL_02 = H_02Avr - L_02Avr #(maxHigh - 2 %) - (maxLow - 2 %)
    P_HL_02_Prnt = round(HL_02/price*100,2) # percentage difference current Price and delta High(-0.2%) - Low(-0.2%) For Profit Markup
    if P_HL_02_Prnt > 1: P_HL_02_Prnt = 1 # if more then 1% - it is temporary !!!!!!!!!?????????

    return P_HL_02_Prnt
