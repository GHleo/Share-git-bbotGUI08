import tkinter as tk
from datetime import datetime as dt
import sqlite3
import threading
from binance.client import Client
import keys
import time
import configGlb as cnf
import ta as ta
# import requests  # for making http requests to binance
# import json  # for parsing what binance sends back to us
# import pandas as pd  # for storing and manipulating the data we get back
# import matplotlib.pyplot as plt
from tkinter import messagebox as msg
import queriesToDB as db
from misc import adjust_to_step, macdSignalCross, newOrderM


client = Client(keys.apikey, keys.apisecret)
limits = cnf.bot.exchangeInfo()  # Получаем лимиты пары с биржи
balances = {}

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
def taTradeMACD(w1th_scrol,w2th_scrol,w3th_scrol, pb00_):
    conn = sqlite3.connect('binance_app088.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    db.make_initial_tables_appTA(cursor)  # table for MACD alg
    global balances
    global isBuing, isSelling
    isSelling, isBuing = True, True
    cnf.longSQLiteGlb, cnf.longSQLiteGlbSell = False,False #flag for approve transaction
    # Получаем балансы с биржи по указанным валютам
    for pair_name, pair_obj in cnf.pairsGL.items():
        balances = {balance['asset']: float(balance['free']) for balance in cnf.bot.account()['balances']
                if balance['asset'] in [pair_obj['base'], pair_obj['quote']]}
    w2th_scrol.delete(0.1, tk.END)
    w3th_scrol.delete(0.1, tk.END)
    w3th_scrol.insert(tk.END,'taTradeMACD -> START!!!' + '\n')
    while cnf.loop_AppWrk < cnf.loopGL and cnf.App_freezLong_GL:
        try:
            cnf.isWork_or_Mrg = True
            db.get_open_orders_appTA(cursor)
            order_statusS, order_statusB = True, True
            dtSB, new_orderId = 0,0
            print("Получены неисполненные ордера из БД: {orders}".format(orders=[(order, cnf.orders_infoMACD[order]['order_pair']) for order in cnf.orders_infoMACD]))
            buy_order = [order for order in cnf.orders_infoMACD]
            print('************ taTradeMACD buy_order: ' + str(buy_order))
            #print('************ taTradeMACD type(buy_order): ' + str(type(buy_order)) + '; buy_order: ' + str(buy_order))
# !!!!!!!!!!!!!!!!!!!!!! BOUGHT need SELL !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            if cnf.orders_infoMACD and not isBuing:
                cnf.isWork_or_Mrg = False  # for take on AppMargin
                delay_ = 0.05
                while isSelling:  # while isSelling true
                    sprice = round(float(cnf.bot.tickerPrice(symbol=cnf.symbolPairGL)['price']), 2)
                    print('Sell... MACD While isSelling! ' + str(dt.now().strftime('%H:%M:%S'))+ '\n')
                    sotype, sbverified, sbought, ssprice, sfsprice, buyorder, selorder, sgotqty, sincomeV,sincomeP, sprftmarkup, ssloss, spname, CURR_LIMITS, bdtSec, isBub = SELL(cnf.orders_infoMACD,sprice)
                    time_passedM = round((int(time.time()) - bdtSec) / 60, 2)
                    if sbverified and sotype == 'buy':
                        print("Sell... MACD -isSelling- Current -> Aim price " + str(ssprice))
                        w2th_scrol.delete(0.1, tk.END)
                        w2th_scrol.insert(tk.END, 'Sell... MACD; Profit/StopLoss -> ' + str(sprftmarkup) + '/' + str(ssloss) + '\n' + 'Bought    -> ' + str(sbought) + '\n' + 'Curr rate ->        ' + str(sprice) +
                                          '\n' + 'Aim price -> ' + str(ssprice) + '\n' + 'Forc sell -> ' + str(sfsprice) + '\n' + 'Income(%) -> ' + str(sincomeP) + '\n' + str(cnf.SELLlng_LIFE_TIME_MIN)+' min. limit; ..... time passed min. ' + str(time_passedM) + '\n')
# !!!!!!!!!!!!!!!!!! Sell MARKET with STOP LOSS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                        if cnf.isMRKT_GL:
                            if time_passedM > cnf.SELLlng_LIFE_TIME_MIN and isBub:
                                new_order = newOrderM(pair_name_=spname, got_qty_=sgotqty, CURR_LIMITS_=CURR_LIMITS, need_cost_=0, side_='SELL', type_='MARKET', mode='trade')
                                db.store_sell_order_appTA(cursor, conn, buyorder, new_order['orderId'], sgotqty,sprftmarkup)
                                if 'orderId' in new_order:
                                    print("Sell(App)... MACD -MARKET- Создан рыночный ордер на продажу {new_order}".format(new_order=new_order))
                                    w3th_scrol.insert(tk.END, 'SellBUB... Price-> ' + str(sprice) + '; Income($)-> ' + str(sincomeV) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '\n\n')
                                    db.update_sell_rate_appTA(cursor, conn, buyorder, ssprice, sincomeV,1)  # sorder is buy_order_id
                                    cnf.loop_AppWrk += 1
                                    cnf.App_freezLong_GL = False
                                    break
                                else:
                                    w3th_scrol.insert(tk.END,'SellBub... new_order Failed!!! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                    cnf.loop_AppWrk = cnf.loopGL + 1
                                    break
                            if sprice > ssprice:
                                new_order = newOrderM(pair_name_=spname, got_qty_=sgotqty, CURR_LIMITS_=CURR_LIMITS, need_cost_=0, side_='SELL', type_='MARKET', mode='trade')
                                db.store_sell_order_appTA(cursor, conn, buyorder, new_order['orderId'], sgotqty,sprftmarkup)
                                if 'orderId' in new_order:
                                    print("Sell(App)... MACD -MARKET- Создан рыночный ордер на продажу {new_order}".format(new_order=new_order))
                                    w3th_scrol.insert(tk.END, 'Sell(App)... Price-> ' + str(sprice) + '; Income($)-> ' + str(sincomeV) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '\n\n')
                                    db.update_sell_rate_appTA(cursor, conn, buyorder, ssprice, sincomeV,1)  # sorder is buy_order_id
                                    cnf.loop_AppWrk += 1
                                    cnf.App_freezLong_GL = False
                                    break
                                else:
                                    w3th_scrol.insert(tk.END,'Sell... new_order Failed!!! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                    cnf.loop_AppWrk = cnf.loopGL + 1
                                    break
                            if sfsprice > sprice and ssloss > 0:
                                new_order = newOrderM(pair_name_=spname, got_qty_=sgotqty, CURR_LIMITS_=CURR_LIMITS, need_cost_=0, side_='SELL', type_='MARKET', mode='trade')
                                db.store_sell_order_appTA(cursor, conn, buyorder, new_order['orderId'], sgotqty,sprftmarkup)
                                if 'orderId' in new_order:
                                    print("Sell...-Stop loss!- Short Trend -MARKET- Создан рыночный ордер на продажу  {new_order}".format(new_order=new_order))
                                    w3th_scrol.insert(tk.END, 'Force Sell... Price-> ' + str(sfsprice) + '; Income($)-> ' + str(sincomeV) + '; ' +str(dt.now().strftime('%H:%M:%S')) + '\n\n')
                                    db.update_sell_rate_appTA(cursor, conn, buyorder, sprice, sincomeV, 0)
                                    cnf.loop_AppWrk += 1
                                    cnf.App_freezLong_GL = False
                                    break
                                else:
                                    w3th_scrol.insert(tk.END,'Force Sell... new_order Failed!!! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                    cnf.loop_AppWrk = cnf.loopGL + 1
                                    break
# !!!!!!!!!!!!!!!!!! Sell LIMIT with STOP LOSS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                        if cnf.isLMT_GL:
# ---------------------- Check created sell order (there is in table) or not
                            if not selorder:  # if is not order sell yet
                                new_order = newOrderM(pair_name_=spname, got_qty_=sgotqty, CURR_LIMITS_=CURR_LIMITS,need_cost_=ssprice, side_='SELL', type_='LIMIT',mode='trade')  # sell
                                db.store_sell_order_appTA(cursor, conn, buyorder, new_order['orderId'], sgotqty, sprftmarkup)
                                if 'orderId' in new_order and cnf.longSQLiteGlbSell: # check if Create order and Write to data base
                                    new_orderId = new_order['orderId']  # orderID
                                    time.sleep(2)
                                    w3th_scrol.insert(tk.END, 'Sell(App)... CREATED!' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                    dtSB = int(time.time())
                                else:
                                    w3th_scrol.insert(tk.END, 'Sell(App)... Create and write FALSE! cnf.longSQLiteGlbSell = ' + str(cnf.longSQLiteGlbSell) +'; ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                    #msg.showinfo("taTradeMACD", 'Sell(App)... Some problem when creating a new order!')
                            else:
                                new_orderId = selorder
                                w3th_scrol.insert(tk.END, 'Sell(App)... Created order from DB! orderId = ' + str(selorder) +'; ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                dtSB = int(time.time())
                            print('Sell... MACD -isSelling- selorder: ' + str(selorder) + '; buyorder: ' + str(buyorder) + '; new_orderId: ' + str(new_orderId))
                            if new_orderId:
                                isForce = 1 # if 1 - not force sell else force sell
                                while order_statusS:
                                    slprice = round(float(cnf.bot.tickerPrice(symbol=cnf.symbolPairGL)['price']), 2)
                                    w2th_scrol.delete(0.1, tk.END)
                                    sotype, sbverified, sbought, ssprice, sfsprice, buyorder, selorder, sgotqty, sincomeV, sincomeP,sprftmarkup, ssloss, spname, CURR_LIMITS, bdtSec, isBub = SELL(cnf.orders_infoMACD, slprice)  # -15-
                                    sellstatus,time_passedS, time_passedM = OrderInfo(spname,new_orderId,dtSB)
                                    print("Sell(App)... ShortTrend -LIMIT(while order_statusS)- Order status  {os};".format(os=sellstatus))
                                    if sellstatus == 'FILLED':
                                        db.update_sell_rate_appTA(cursor, conn, buyorder, slprice, sincomeV, isForce)
                                        if cnf.longSQLiteGlbSell:
                                            w3th_scrol.insert(tk.END, '............ COMPLETE! ' + str(dt.fromtimestamp(int(time.time()))) + '\n' + 'Income($)-> ' + str(sincomeV) + '; ' + 'Time passed min. -> ' + str(time_passedM) + '\n\n')
                                        else:
                                            msg.showinfo("taTradeMACD",'Sell... Some problem when write to DB!')
                                        cnf.loop_AppWrk += 1
                                        isSelling = False
                                        cnf.App_freezLong_GL = False
                                        break
                                    if sellstatus == 'NEW':
                                        print('Sell(App)... MACD -LIMIT- order_status  {os}; datetime {dt}; time passed {tp} min.'.format(os=sellstatus, dt=dt.fromtimestamp(int(time.time())),tp=time_passedM))
                                        w2th_scrol.insert(tk.END, 'Sell... MACD -LIMIT-; Profit/SLoss -> ' + str(sprftmarkup) +'/'+ str(ssloss) + '\n' + 'Bought    -> ' + str(sbought) + '\n' + 'Curr rate ->        ' + str(slprice) +
                                          '\n' + 'Aim price -> ' + str(ssprice) + '\n' + 'Forc sell -> ' + str(sfsprice) + '\n' + 'Income(%) -> ' + str(sincomeP) + '\n'+ '...... Time passed min.-> ' + str(time_passedM) + '\n')
                                        # Прошло больше времени, чем разрешено держать ордер
                                        if time_passedM > cnf.SELLlng_LIFE_TIME_MIN and isBub and sellstatus != 'PARTIALLY_FILLED':
                                            w2th_scrol.insert(tk.END, 'Time passed ->  ' + str(time_passedM) + ' min. Exit Order: ' + str(new_orderId) + '\n')
                                            cancel = cnf.bot.cancelOrder(symbol=spname, orderId=new_orderId) # Отменяем ордер на бирж
                                            time.sleep(2)
                                            #db.update_sell_lmt_appTA(cursor, conn, buyorder, cancel['orderId'])  # UPDATE sell_order_Id(cancel) same record in store_sell_order_appTA
                                            # Если удалось отменить ордер, удаляем информацию из БД
                                            if 'orderId' in cancel: # and cnf.longSQLiteGlbSell:
                                                w3th_scrol.insert(tk.END, 'Sell... Order Cancel SUCCESSFULLY! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                                new_order = newOrderM(pair_name_=spname, got_qty_=sgotqty,CURR_LIMITS_=CURR_LIMITS, need_cost_=0,side_='SELL', type_='MARKET', mode='trade')
                                                new_orderId = new_order['orderId']
                                                if new_orderId:
                                                    w3th_scrol.insert(tk.END,'SellBUB... CREATE Market Order! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                                else:
                                                    w2th_scrol.insert(tk.END,'SellBUB... new_order Failed!!! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                                    #msg.showinfo("taTradeMACD",'SellBUB... Some problem when creating a new order!')
                                            else:
                                                w2th_scrol.insert(tk.END, 'SellBUB... Order Cancel FAILD! ' + str(dt.fromtimestamp(int(time.time()))) + '\n')
                                                #msg.showinfo("taTradeMACD",'SellBUB... Some problem when Cancel order!')
                                    if sellstatus == 'PARTIALLY_FILLED':
                                        w2th_scrol.insert(tk.END, 'Sell(App)... MACD -LIMIT- Status is ->  ' + str(sellstatus) + '; dt -> ' + str(dt.fromtimestamp(int(time.time()))) + '\n')
                                    if sellstatus == 'CANCELED':
                                        w2th_scrol.insert(tk.END, 'CANCELED!!! new_orderId:  ' + str(new_orderId) + '; dt -> ' + str(dt.fromtimestamp(int(time.time()))) + '\n')
                                        isSelling = False
                                        cnf.App_freezLong_GL = False
                                        break
# ----------------------------- Sell LIMIT when STOP LOSS ----------------------
                                    if sfsprice > slprice and ssloss > 0 and sellstatus != 'PARTIALLY_FILLED':
                                        print("Force Sell(App)... MACD -LIMIT- sfsprice {sl} - slprice {cr}".format(sl=sfsprice, cr=slprice))
                                        cancelF = cnf.bot.cancelOrder(symbol=spname,orderId=new_orderId)  # Отменяем ордер на бирже
                                        time.sleep(2)
                                        if 'orderId' in cancelF:
                                            w3th_scrol.insert(tk.END, 'Force Sell... Order Cancel SUCCESSFULLY! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                            new_orderF = newOrderM(pair_name_=spname, got_qty_=sgotqty,CURR_LIMITS_=CURR_LIMITS, need_cost_=0,side_='SELL', type_='MARKET',mode='trade')  # force sell
                                            time.sleep(4)
                                            #db.update_sell_lmt_appTA(cursor, conn, buyorder, new_orderF['orderId'])  #??????? UPDATE sell_order_Id(Force sell) same record in store_sell_order_appTA
                                            isForce = 0
                                            new_orderId = new_orderF['orderId']
                                            if new_orderId:
                                                w3th_scrol.insert(tk.END, 'Force Sell... CREATE Market Order! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                            else:
                                                w2th_scrol.insert(tk.END,'Force Sell... new_order Failed!!! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                                #msg.showinfo("taTradeMACD",'Force Sell... Some problem when creating a new order!')
                                        else:
                                            w2th_scrol.insert(tk.END,'Force Sell... Order Cancel FAILD!!! ' + str(dt.fromtimestamp(int(time.time()))) + '\n')
                                            #msg.showinfo("taTradeMACD",'Force Sell... Some problem when cancel order!')
                                    time.sleep(6)  # 6sec
                            else:
                                w3th_scrol.insert(tk.END, 'Sell(App)... -LIMIT- new_order Failed!!! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                #cnf.loop_AppWrk = cnf.loopGL + 1
                                #break
                        #if cnf.HSTRLoop_GL: cnf.App_freezLong_GL = False # if run HSTREmulate
                        if not isSelling: break  # Exit from loop isSelling
                    else:
                        print('ERROR Sell... MACD - Buy do not accept (not verified) !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ')
                    thread = threading.Thread(target=run_progressbar(pb00_, delay_))
                    thread.start()
# !!!!!!!!!!!!!!!!!!!!!!!!!!! need BUY  Если остались пары, по которым нет текущих торгов !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            else:
                print('else MACD + isBuing-> ', isBuing)
                while isBuing and cnf.App_freezLong_GL:
                    klines = cnf.bot.klines(symbol=cnf.symbolPairGL,interval=cnf.KlineGL,limit=cnf.KLINES_LIMITS)
                    klinesMinusLast = klines[:len(klines) - int(cnf.USE_OPEN_CANDLES)]
                    closes = [float(x[4]) for x in klinesMinusLast]
                    cprice= round(float(cnf.bot.tickerPrice(symbol=cnf.symbolPairGL)['price']), 2)
                    macd, macdsignal, macdhist = ta.MACD(closes, 7, 14, 9)
                    Ups, Dns = macdSignalCross(macd, macdsignal)
                    if cnf.isWork_or_Mrg:  # one scrool for two algo - if work margin this take off
                        w1th_scrol.delete(0.1, tk.END)
                        w1th_scrol.insert(tk.END, '   ### Working App use MACD! (taTradeMACD) ###' + '\n' + '      (When selling in progress it freez!) ' + '\n\n')
                        w1th_scrol.insert(tk.END,' MACD -> EMA Short/Long/Signal -> 7/14/9' + '\n\n' + 'KLINES_LIMITS(period)-> ' + str(cnf.KLINES_LIMITS) + '\n' + 'TIMEFRAME(in minutes)-> ' + str(cnf.KlineGL) + '\n')
                        w1th_scrol.insert(tk.END, 'Buy  LIFE_TIME_MIN-> ' + str(cnf.BUYlng_LIFE_TIME_MIN) + '\n' + 'Sell LIFE_TIME_MIN-> ' + str(cnf.SELLlng_LIFE_TIME_MIN) + '\n')
                        w1th_scrol.insert(tk.END, '------------------------------------------------' + '\n\n')
                        w1th_scrol.insert(tk.END, 'Is Market/Limit? -> ' + str(cnf.isMRKT_GL) + '/' + str(cnf.isLMT_GL) + '\n' + 'Is cross Up?     -> ' + str(Ups) + '\n' + 'Rate             -> ' + str(cprice) + '\n')
                        w1th_scrol.insert(tk.END,'------------------------------------------------' + '\n')
                    bpname, bmyamount, bsellLMT, bprofitmarkup, bstoploss, spendsum, CURR_LIMITS, bdt = BUY(cprice)  # -9-
# !!!!!!!!!!!!!!!!!!!!!! BUY MARKET if crossed Up !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    if Ups and cnf.isMRKT_GL:  # if SHORT TREND or STARTED from HSTREmulate and Market
                        print('Buy(App)... MACD -MARKET-  if UPS {iu};  isMRKT_GL  {m}'.format(iu=Ups, m=cnf.isMRKT_GL))
                        new_order = newOrderM(pair_name_=bpname, got_qty_=bmyamount, CURR_LIMITS_=CURR_LIMITS, need_cost_=0, side_='BUY', type_='MARKET', mode='trade')
                        db.add_new_order_buy_appTA(cursor, conn, bpname, new_order['orderId'], bmyamount, cprice,bprofitmarkup, bstoploss, 0, 'market')  # -10-
                        w3th_scrol.insert(tk.END, 'Buy(App)... CREATE MAKD -MARKET- Pair->' + str( bpname) + '\n' + 'Price-> ' + str(cprice) + '; Amount: ' + str(bmyamount) + '; ' + str(dt.fromtimestamp(int(time.time()))) + '\n')
                        if 'orderId' in new_order:
                            db.update_buy_rate_appTA(cursor, conn, new_order['orderId'], cprice)
                            w3th_scrol.insert(tk.END, '........... COMPLETE  ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                            #isBuing = False
                            break  # terminate loop -isBuing-
                        else:
                            w3th_scrol.insert(tk.END, 'Buy(App)... MAKD -MARKET- create new_order Failed!!! ' + str(dt.now().strftime('%H:%M:%S')) + '\n\n')
                            #isBuing = False
                            break  # terminate loop -isBuing-

# !!!!!!!!!!!!!!!!!!!!!! BUY LIMIT with TIMER if fast fall last candel !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    if (Ups and cnf.isLMT_GL) or (buy_order and cnf.isLMT_GL):  # if Short trend or started from HSTREmulate and Limit
                        #need_priceLMT = round(cprice - cnf.nLMTautoDnLng_GL,2)  # 5$ buy low on base crypto ????????? we need correcting sellLMT
                        if cnf.nLMT_GL_CheckB == 0:
                            need_priceLMT = round(cprice - cnf.nLMT_GL, 2)
                        else:
                            need_priceLMT = round(cprice - cnf.nLMTautoDnLng_GL,2)
                        print('taTradeMACD()... cnf.nLMT_GL_CheckB: ' + str(cnf.nLMT_GL_CheckB) + '; cnf.nLMT_auto: ' + str(cnf.nLMTautoDnLng_GL) + '; cnf.nLMT_MrgGL: ' + str(cnf.nLMT_GL))
                        if not buy_order:  # if is not order buy yet    
                            new_order = newOrderM(pair_name_=bpname, got_qty_=bmyamount, CURR_LIMITS_=CURR_LIMITS, need_cost_=need_priceLMT, side_='BUY', type_='LIMIT', mode='trade')
                            db.add_new_order_buy_appTA(cursor, conn, bpname, new_order['orderId'], bmyamount,need_priceLMT, bprofitmarkup, bstoploss, bsellLMT,'limit')  # -10-
                            if 'orderId' in new_order and cnf.longSQLiteGlb: # check if Create order and Write to data base
                                new_orderId = new_order['orderId']
                                w3th_scrol.insert(tk.END, 'Buy(App)... CREATED and write to db; MACD LIMIT; ' + str(bpname) + '\nPrice -> ' + str(need_priceLMT) + '; Amount -> ' + str(bmyamount) + '; ' + str(dt.fromtimestamp(int(time.time()))) +
                                                  '; cnf.nLMTautoDnLng_GL: ' + str(cnf.nLMTautoDnLng_GL)+'\n')
                                #w3th_scrol.insert(tk.END, 'Buy(App)... test new_orderId: ' + str(type(new_orderId) + str(new_orderId)) + '\n')
                                dtSB = int(time.time())
                            else:
                                w3th_scrol.insert(tk.END, 'Buy(App)... CREATED and write FALSE! ' + str(dt.now().strftime('%H:%M:%S')) + '\n\n')
                                cnf.App_freezLong_GL = False  # Exit from function
                                isBuing = False
                                break
                        else:
                            new_orderId = str(buy_order[0])
                            w3th_scrol.insert(tk.END, 'Buy(App)... CREATE Order Repeated! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                            #w3th_scrol.insert(tk.END, 'Buy(App)... test buy_order: ' + str(type(buy_order)) + str(buy_order[0]) + '\n')
                            dtSB = int(time.time())
                        if new_orderId:
                            while order_statusB: #and not cnf.orders_infoShTr:
                                bprice = round(float(cnf.bot.tickerPrice(symbol=cnf.symbolPairGL)['price']), 2)
                                w2th_scrol.delete(0.1, tk.END)
                                bpname, bmyamount, bsellLMT, bprofitmarkup, bstoploss, spendsum, CURR_LIMITS, bdt = BUY(bprice)  # -9-
                                order_status, time_passedS, time_passedM = OrderInfo(bpname,new_orderId,dtSB)
                                if order_status == 'FILLED':
                                    db.update_buy_rate_appTA(cursor, conn, new_orderId, need_priceLMT)
                                    w3th_scrol.insert(tk.END, '........... COMPLETE ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                    isBuing = False
                                    break
                                if order_status == 'NEW':
                                    w2th_scrol.insert(tk.END,'Buy(App)...MACD -LIMIT- Status NEW \nCurrent rate-> ' + str(bprice) + '\nAim         -> ' + str(need_priceLMT) + '\n..... time passed min. ' + str(time_passedM) + '\n')
                                    print('Buy(App)...MACD -LIMIT- Status NEW; Current rate-> ' + str(bprice) + '; Aim-> ' + str(need_priceLMT) + '\n..... time passed min. ' + str(time_passedM) + '\n')
                                    if time_passedM > cnf.BUYlng_LIFE_TIME_MIN and order_status != 'PARTIALLY_FILLED':
                                        print("Buy(App)... MACD -LIMIT- Ордер {order} пора отменять, прошло {passed:0.2f} min.".format(order=new_orderId, passed=time_passedM))
                                        cancel = cnf.bot.cancelOrder(symbol=bpname, orderId=new_orderId) # Отменяем ордер на бирже
                                        time.sleep(2)
                                        db.update_buy_Cancel_appTA(cursor, conn, new_orderId)
                                        if ('orderId' in cancel) and cnf.longSQLiteGlb:
                                            print("Buy(App)... MACD -LIMIT- Ордер: {order} был успешно отменен".format(order=new_orderId))
                                            w3th_scrol.insert(tk.END,'Buy(App)... Order Cancel SUCCESSFULLY! orderID: ' + str(cancel['orderId']) + str('; ') + str(dt.now().strftime('%H:%M:%S')) + '\n\n')
                                            cnf.App_freezLong_GL = False  # Exit from function
                                            isBuing = False
                                            break
                                        else:
                                            w3th_scrol.insert(tk.END, 'Buy(App)... MACD -LIMIT- Failed Cancel order or Write DB! order: ' + str(cancel))
                                            print('Buy(App)... MACD -LIMIT- Cancel order Failed! order: ' + str(cancel) + '\n')
                                            #msg.showinfo("taTradeMACD",'Buy(App)... MACD Failed Cancel order or Write DB!')
                                            isBuing = False
                                            break
                                    print('buy(App)... ShortTrend -LIMIT- order_status  {os}; datetime {dt};'.format(os=order_status, dt=dt.fromtimestamp(int(time.time()))))
                                    #w2th_scrol.insert(tk.END, 'buy(App)...ShortTrend -LIMIT- Status is ->  ' + str(order_status) + '; dt -> ' + str(dt.fromtimestamp(int(time.time()))) + '\n')
                                if order_status == 'PARTIALLY_FILLED':
                                    print("Buy(App)... MACD -LIMIT- Ордер {order} частично исполнен, ждем завершения".format(order=new_orderId))
                                    w2th_scrol.insert(tk.END,'Buy(App)... MACD-LIMIT- status i PARTIALLY_FILLED ' + '\n..... time passed min. ' + str(time_passedM) + '; dt -> ' + str(dt.fromtimestamp(int(time.time()))) + '\n')
                                if order_status == 'CANCELED':
                                    db.update_buy_Cancel_appTA(cursor, conn, new_orderId)
                                    w2th_scrol.insert(tk.END,'Buy(App)... MACD -LIMIT- Status is -> CANCELED! '  + str(dt.fromtimestamp(int(time.time()))) + '\n')
                                    cnf.App_freezLong_GL = False  # Exit from function
                                    isBuing = False
                                    break
                                #w2th_scrol.insert(tk.END, 'Buy... MACD -LIMIT- Status-> ' + str(order_status) + '; time passed-> ' + str(time_passedM) + str(' min.') + '\n')
                                time.sleep(6)  # 6sec
                        else:
                            w3th_scrol.insert(tk.END, 'Buy(App)... MAKD -LIMIT- create new_order Failed!!!  ' + str(dt.now().strftime('%H:%M:%S')) + '\n\n')
                            break
                    if not isBuing: break  # Exit from loop isBuing

                    thread = threading.Thread(target=run_progressbar(pb00_, cnf.chVarDelay_GL))
                    thread.start()
            if cnf.loop_AppWrk >= cnf.loopGL:
                w2th_scrol.insert(tk.END, 'taTradeMACD TERMINATE! Loop = ' + str(cnf.loop_AppWrk) +'; '+ str(dt.now().strftime('%H:%M:%S'))+ '\n')
                cnf.App_freezLong_GL = False
        except Exception as e:
            print("time.sleep(10) ERROR taTradeMACD().... from WHILE cnf.loop_AppEmulShTr {}".format(e))
            cursor.close()
            time.sleep(10)
            cursor = conn.cursor()
            print('AppWork()... exception!!!!!!!!!! conn: ' + str(conn) + '; cursor: ' + str(cursor))
            continue
    w2th_scrol.insert(tk.END,'taTradeMACD TERMINATE - End Function! loop_AppWrk = ' + str(cnf.loop_AppWrk) + '; ' + str(dt.now().strftime('%H:%M:%S'))+ '\n')
    cursor.close()
@thread
def taTradeShTrend(w1th_scrol,w2th_scrol,w3th_scrol, pb00_):
    conn = sqlite3.connect('binance_app088.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    db.make_initial_tables_appTA_ShTr(cursor)  # table for Short Trend alg
    isSelling, isBuing = True, True
    global balances
    cnf.longSQLiteGlb, cnf.longSQLiteGlbSell = False,False #flag for approve transaction
    # Получаем балансы с биржи по указанным валютам
    for pair_name, pair_obj in cnf.pairsGL.items():
        balances = {balance['asset']: float(balance['free']) for balance in cnf.bot.account()['balances']
                if balance['asset'] in [pair_obj['base'], pair_obj['quote']]}
    #print("taTradeShTrend... Баланс {balance}".format(balance=["{k}:{bal:0.8f}".format(k=k, bal=balances[k]) for k in balances]))
    w2th_scrol.delete(0.1, tk.END)
    w3th_scrol.delete(0.1, tk.END)
    w3th_scrol.insert(tk.END,'taTradeShTrend -> START!!!!\n')
    while cnf.loop_AppWrkShTr < cnf.loopGL and cnf.App_freezLong_GL:
        try:
            cnf.isWork_or_Mrg_ShTr = True
            order_statusS, order_statusB = True, True
            new_orderId,new_orderFS,dtSB = 0,0,0
            db.get_open_orders_appTA_ShTr(cursor) #Получаем все неисполненные ордера по БД SELECT, fill cnf.orders_infoShTr
            buy_order = [order for order in cnf.orders_infoShTr] # buy_order_id for limit buy
            print('************ taTradeShTrend buy_order: ' + str(buy_order))
            print("Получены неисполненные ордера из БД: {orders}".format(orders=[(order, cnf.orders_infoShTr[order]['order_pair']) for order in cnf.orders_infoShTr]))
#!!!!!!!!!!!!!!!!!!!!!! BOUGHT need SELL !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            if cnf.orders_infoShTr and not isBuing:
                cnf.isWork_or_Mrg_ShTr = False
                delay_ = 0.05
                while isSelling:  # while isSelling true e
                    sprice = round(float(cnf.bot.tickerPrice(symbol=cnf.symbolPairGL)['price']), 2)
                    print('Sell... Short Trend While isSelling! ' + str(dt.now().strftime('%H:%M:%S'))+ '\n')
                    sotype, sbverified, sbought, ssprice, sfsprice, buyorder, selorder, sgotqty, sincomeV,sincomeP, sprftmarkup, ssloss, spname, CURR_LIMITS, bdtSec, isBub = SELL(cnf.orders_infoShTr, sprice) # -14-
                    time_passedM = round((int(time.time()) - bdtSec) / 60, 2)
                    if sbverified and sotype == 'buy':
                        print("Sell... Short Trend -isSelling- Current -> Aim price " + str(ssprice))
                        w2th_scrol.delete(0.1, tk.END)
                        w2th_scrol.insert(tk.END, 'Sell... Short Trend; Profit/StopLoss -> ' + str(sprftmarkup) + '/' + str(ssloss) + '\nBought    -> ' + str(sbought) + '\nCurr rate ->        ' + str(sprice) +
                                          '\nAim price -> ' + str(ssprice) + '\nForc sell -> ' + str(sfsprice) + '\nIncome(%) -> ' + str(sincomeP) + '\nTime passed min. -> ' + str(time_passedM) + '\n')
# !!!!!!!!!!!!!!!!!! Sell MARKET with STOP LOSS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                        if cnf.isMRKT_GL:
                            if time_passedM > cnf.SELLlng_LIFE_TIME_MIN and isBub:
                                new_order = newOrderM(pair_name_=spname, got_qty_=sgotqty, CURR_LIMITS_=CURR_LIMITS, need_cost_=0, side_='SELL', type_='MARKET', mode='trade')
                                db.store_sell_order_appTA_ShTr(cursor, conn, buyorder, new_order['orderId'],sgotqty, sprftmarkup)
                                if 'orderId' in new_order:
                                    w3th_scrol.insert(tk.END, 'SellBUB... Price-> ' + str(sprice) + '; Income($)-> ' + str(sincomeV) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '\n\n')
                                    db.update_sell_rate_appTA_ShTr(cursor, conn, buyorder, ssprice, sincomeV,1) # sorder is buy_order_id
                                    cnf.loop_AppWrkShTr += 1
                                    cnf.App_freezLong_GL = False
                                    break
                                else:
                                    w3th_scrol.insert(tk.END, 'SellBub... new_order Failed!!! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                    cnf.loop_AppWrkShTr = cnf.loopGL + 1 # Exit from function
                                    break
                            if sprice > ssprice:
                                new_order = newOrderM(pair_name_=spname, got_qty_=sgotqty, CURR_LIMITS_=CURR_LIMITS, need_cost_=0, side_='SELL', type_='MARKET', mode='trade')
                                db.store_sell_order_appTA_ShTr(cursor, conn, buyorder, new_order['orderId'],sgotqty, sprftmarkup)
                                if 'orderId' in new_order:
                                    w3th_scrol.insert(tk.END, 'Sell(App)... Price-> ' + str(sprice) + '; Income($)-> ' + str(sincomeV) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '\n\n')
                                    db.update_sell_rate_appTA_ShTr(cursor, conn, buyorder, ssprice, sincomeV,1) # sorder is buy_order_id
                                    cnf.loop_AppWrkShTr += 1
                                    cnf.App_freezLong_GL = False
                                    break
                                else:
                                    w3th_scrol.insert(tk.END, 'Sell(App)... new_order Failed!!! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                    cnf.loop_AppWrkShTr = cnf.loopGL + 1 # Exit from function
                                    break
                            if sfsprice > sprice and ssloss > 0:
                                new_order = newOrderM(pair_name_=spname, got_qty_=sgotqty, CURR_LIMITS_=CURR_LIMITS, need_cost_=0, side_='SELL', type_='MARKET', mode='trade')
                                db.store_sell_order_appTA_ShTr(cursor, conn, buyorder, new_order['orderId'],sgotqty, sprftmarkup)
                                if 'orderId' in new_order:
                                    w3th_scrol.insert(tk.END, 'Force Sell... Price-> ' + str(sfsprice) + '; Income($)->' + str(sincomeV) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '\n\n')
                                    db.update_sell_rate_appTA_ShTr(cursor, conn, buyorder, sprice, sincomeV, 0)
                                    cnf.loop_AppWrkShTr += 1
                                    cnf.App_freezLong_GL = False
                                    break
                                else:
                                    w3th_scrol.insert(tk.END, 'Force Sell... new_order Failed!!! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                    cnf.loop_AppWrkShTr = cnf.loopGL + 1 # Exit from function
                                    break
# !!!!!!!!!!!!!!!!!! Sell LIMIT with STOP LOSS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                        if cnf.isLMT_GL:
# ---------------------- Check created sell order (there is in table) or not
                            if not selorder: # if is not order sell yet
                                new_order = newOrderM(pair_name_=spname, got_qty_=sgotqty, CURR_LIMITS_=CURR_LIMITS,need_cost_=ssprice, side_='SELL', type_='LIMIT', mode='trade') # sell
                                time.sleep(2)
                                db.store_sell_order_appTA_ShTr(cursor, conn, buyorder, new_order['orderId'], sgotqty, sprftmarkup)
                                if 'orderId' in new_order and cnf.longSQLiteGlbSell:
                                    w3th_scrol.insert(tk.END, 'Sell(App)... CREATE! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                    new_orderId = new_order['orderId'] #orderID
                                    dtSB = int(time.time())
                                else:
                                    w3th_scrol.insert(tk.END, 'Sell(App)... Create and write FALSE! cnf.longSQLiteGlbSell = ' + str(cnf.longSQLiteGlbSell) +'; ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                    #msg.showinfo("taTradeShTrend", 'Sell(App)... Some problem when creating a new order!')
                            else:
                                w3th_scrol.insert(tk.END, 'Sell(App)... Created order from DB! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                new_orderId = selorder
                                dtSB = int(time.time())
                            print('Sell... Short Trend -isSelling- selorder: ' + str(selorder) + '; buyorder: ' + str(buyorder)+ '; new_orderId: ' + str(new_orderId))
                            if new_orderId:
                                isForce = 1 # if 1 - not force sell else force sell
                                while order_statusS:
                                    slprice = round(float(cnf.bot.tickerPrice(symbol=cnf.symbolPairGL)['price']), 2)
                                    w2th_scrol.delete(0.1, tk.END)
                                    sotype, sbverified, sbought, ssprice, sfsprice, buyorder, selorder, sgotqty, sincomeV,sincomeP, sprftmarkup, ssloss, spname, CURR_LIMITS, bdtSec, isBub = SELL(cnf.orders_infoShTr, slprice)  # -14-
                                    sellstatus,time_passedS, time_passedM = OrderInfo(spname,new_orderId,dtSB)
                                    print("Sell(App)... ShortTrend -LIMIT(while order_statusS)- Order status  {os};".format(os=sellstatus))
                                    if sellstatus == 'FILLED':
                                        db.update_sell_rate_appTA_ShTr(cursor, conn, buyorder, ssprice, sincomeV,isForce)
                                        if cnf.longSQLiteGlbSell:
                                            w3th_scrol.insert(tk.END, '............ COMPLETE! ' + str(dt.now().strftime('%H:%M:%S')) + '\n' + 'Income($)-> ' + str(sincomeV) + '; CRate: ' + str(slprice) + '; Time passed min. -> ' + str(time_passedM) + '\n\n')
                                        else:
                                            msg.showinfo("taTradeShTrend",'Sell... Some problem when write to DB!')
                                        cnf.loop_AppWrkShTr+= 1
                                        isSelling = False #exit from isSelling
                                        cnf.App_freezLong_GL = False
                                        break
                                    if sellstatus == 'NEW':
                                        w2th_scrol.insert(tk.END, 'Sell...ShortTrend -LIMIT- Profit/SLoss -> ' + str(sprftmarkup) + '/' + str(ssloss)+ '\n' + 'Bought    -> ' + str(sbought)+ '\n' + 'Curr rate ->        ' + str(slprice) +
                                          '\n' + 'Aim price -> ' + str(ssprice) + '\n' + 'Forc sell -> ' + str(sfsprice) + '\n' + 'Income(%) -> ' + str(sincomeP) + '\n'+ '...... Time passed min.-> ' + str(time_passedM) + '\n')
                                        # Прошло больше времени, чем разрешено держать ордер
                                        if time_passedM > cnf.SELLlng_LIFE_TIME_MIN and isBub and sellstatus != 'PARTIALLY_FILLED':
                                            w2th_scrol.insert(tk.END, 'Time passed ->  ' + str(time_passedM) + ' min. Exit Order: ' + str(new_orderId) + '\n')
                                            cancel = cnf.bot.cancelOrder(symbol=spname, orderId=new_orderId) # Отменяем ордер на бирж
                                            #db.update_sell_lmt_appTA(cursor, conn, buyorder, new_order['orderId'])  # UPDATE sell_order_Id(cancel) same record in store_sell_order_appTA
                                            # Если удалось отменить ордер, удаляем информацию из БД
                                            if 'orderId' in cancel:
                                                w3th_scrol.insert(tk.END, 'Sell.. Order Cancel SUCCESSFULLY! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                                new_order = newOrderM(pair_name_=spname, got_qty_=sgotqty,CURR_LIMITS_=CURR_LIMITS, need_cost_=0,side_='SELL', type_='MARKET', mode='trade')
                                                time.sleep(2)
                                                new_orderId = new_order['orderId']
                                                if new_orderId:
                                                    w3th_scrol.insert(tk.END,'SellBUB... CREATE Market Order. ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                                else:
                                                    w2th_scrol.insert(tk.END,'SellBUB... Create Order FAILD!!! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                                    #msg.showinfo("taTradeShTrend",'SellBUB... Some problem when creating a new order!')
                                            else:
                                                w2th_scrol.insert(tk.END, 'Sell(App)... ShortTrend -LIMIT- Order Cancel FAILD!!! ' + str(dt.fromtimestamp(int(time.time()))) + '\n')
                                                #msg.showinfo("taTradeShTrend",'SellBUB... Some problem when cancel order!')
                                    if sellstatus == 'PARTIALLY_FILLED':
                                        w2th_scrol.insert(tk.END, 'Sell(App)... ShortTrend -LIMIT- Status is ->  ' + str(sellstatus) + '; dt -> ' + str(dt.now().strftime('%H:%M:%S'))+ '\n')
                                    if sellstatus == 'CANCELED':
                                        w2th_scrol.insert(tk.END, 'CANCELED!!! new_orderId:  ' + str(new_orderId) + '; dt -> ' + str(dt.fromtimestamp(int(time.time()))) + '\n\n')
                                        isSelling = False #exit from isSelling
                                        cnf.App_freezLong_GL = False
                                        break
# ----------------------------- Sell LIMIT when STOP LOSS ----------------------
                                    if sfsprice > slprice and ssloss > 0 and sellstatus != 'PARTIALLY_FILLED':
                                        print("Force Sell(App)... ShortTrend -LIMIT- sfsprice {sl} - slprice {cr}".format(sl=sfsprice, cr=slprice))
                                        cancelFS= cnf.bot.cancelOrder(symbol=spname, orderId=new_orderId)
                                        time.sleep(2)
                                        if 'orderId' in cancelFS:
                                            w3th_scrol.insert(tk.END, 'Force Sell.. Order Cancel SUCCESSFULLY! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                            new_orderFS = newOrderM(pair_name_=spname, got_qty_=sgotqty, CURR_LIMITS_=CURR_LIMITS,need_cost_=0, side_='SELL', type_='MARKET', mode='trade') # force sell
                                            time.sleep(2)
                                            #db.update_sell_lmt_appTA(cursor, conn, buyorder, new_orderFS['orderId'])  # UPDATE sell_order_Id(Force sell) same record in store_sell_order_appTA
                                            isForce = 0
                                            new_orderId = new_orderFS['orderId']
                                            if new_orderId:
                                                w3th_scrol.insert(tk.END, 'Force Sell... CREATE Market Order! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                            else:
                                                w2th_scrol.insert(tk.END,'Force Sell... Create Order FAILD!!! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                                #msg.showinfo("taTradeShTrend",'Force Sell... Some problem when creating a new order!')
                                        else:
                                            w2th_scrol.insert(tk.END,'Force Sell... ShortTrend  -LIMIT- Order Cancel FAILD!!! ' + str(dt.fromtimestamp(int(time.time()))) + '\n')
                                            #msg.showinfo("taTradeShTrend",'Force Sell... Some problem when cancel order!')
                                    time.sleep(6)  # 6sec
                            else:
                                w3th_scrol.insert(tk.END, 'Sell... ShortTrend -LIMIT- new_order Failed!!! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                #cnf.loop_AppWrkShTr = cnf.loopGL + 1  # Exit from function
                                #break
                        #if cnf.HSTRLoop_GL: cnf.App_freezLong_GL = False # if run HSTREmulate
                        if not isSelling: break  # Exit from loop isSelling
                    else:
                        print('ERROR Sell... Short Trend - Buy do not accept (not verified) !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ')
                    thread = threading.Thread(target=run_progressbar(pb00_, delay_))
                    thread.start()
# !!!!!!!!!!!!!!!!!!!!!!!!!!! need BUY  Если остались пары, по которым нет текущих торгов !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            else:
                while isBuing and cnf.App_freezLong_GL:
                    #print('buy_cancel', buy_cancel)
                    klines = cnf.bot.klines(symbol=cnf.symbolPairGL,interval=cnf.KlineGL,limit=cnf.KLINES_LIMITS)
                    klinesMinusLast = klines[:len(klines) - int(cnf.USE_OPEN_CANDLES)]
                    opens = [float(x[1]) for x in klinesMinusLast]
                    #high = [float(x[2]) for x in klinesMinusLast]
                    #low = [float(x[3]) for x in klinesMinusLast]
                    closes = [float(x[4]) for x in klinesMinusLast]
                    #volume = [float(x[5]) for x in klinesMinusLast]
                    cprice = round(float(cnf.bot.tickerPrice(symbol=cnf.symbolPairGL)['price']), 2)
                    #dtnow = dt.now().strftime('%H:%M:%S')
                    isUp, isBigUp, isDn, isBigDn = ta.ShortTrend(closes[-int(cnf.fastMoveCount):],opens[-int(cnf.fastMoveCount):])

                    if cnf.isWork_or_Mrg_ShTr:  # one scrool for two algo - if work margin this take off
                        w1th_scrol.delete(0.1, tk.END)
                        w1th_scrol.insert(tk.END, '# Working App use Short Trend! (taTradeShTrend) #\n      (When selling in progress it freez!)\n\n')
                        w1th_scrol.insert(tk.END, 'KLINES_LIMITS(period)-> ' + str(cnf.KLINES_LIMITS) + '\n' + 'TIMEFRAME(in minutes)-> ' + str(cnf.KlineGL) + '\n')
                        w1th_scrol.insert(tk.END, 'Buy  LIFE_TIME_MIN-> ' + str(cnf.BUYlng_LIFE_TIME_MIN) + '\n' + 'Sell LIFE_TIME_MIN-> ' + str(cnf.SELLlng_LIFE_TIME_MIN) + '\n')
                        w1th_scrol.insert(tk.END, '------------------------------------------------' + '\n\n')
                        w1th_scrol.insert(tk.END, 'Is Market/Limit? -> ' + str(cnf.isMRKT_GL) + '/' + str(cnf.isLMT_GL) + '\nIs 3 candles Grow/Down?   -> ' + str(isUp) + '/' + str(isDn)+ '\n')
                        w1th_scrol.insert(tk.END, 'Is last candle Grow/Down? -> ' + str(isBigUp) + '/' + str(isBigDn) + '\nRate   -> ' + str(cprice) + '\n------------------------------------------------\n')
                    bpname, bmyamount, bsellLMT, bprofitmarkup, bstoploss, spendsum, CURR_LIMITS, bdt = BUY(cprice)  # -9-
# !!!!!!!!!!!!!!!!!!!!!! BUY MARKET if fast fall last candel !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    if (isDn or isBigDn) and cnf.isMRKT_GL:  # if SHORT TREND or STARTED from HSTREmulate and Market
                        new_order = newOrderM(pair_name_=bpname, got_qty_=bmyamount, CURR_LIMITS_=CURR_LIMITS, need_cost_=0, side_='BUY', type_='MARKET', mode='trade')
                        db.add_new_order_buy_appTA_ShTr(cursor, conn, bpname, new_order['orderId'], bmyamount,cprice, bprofitmarkup, bstoploss, 0, 'market')  # -10-
                        w3th_scrol.insert(tk.END, 'Buy(App)... ShortTrend CREATE -MARKET- Pair-> ' + str(bpname) + '\n' + 'Price-> ' + str(cprice) + '; Amount: ' + str(bmyamount) + '; ' + str(dt.fromtimestamp(int(time.time()))) + '\n')
                        if 'orderId' in new_order:
                            db.update_buy_rate_appTA_ShTr(cursor, conn, new_order['orderId'], cprice)
                            w3th_scrol.insert(tk.END, 'Buy(App)... COMPLETE!  ' + str(dt.now().strftime('%H:%M:%S')) + '\n' + '\n')
                            isBuing = False
                            break  # terminate loop -isBuing-
                        else:
                            w3th_scrol.insert(tk.END, 'Buy(App)... ShortTrend -MARKET- create new_order Failed!!! ' + str(dt.now().strftime('%H:%M:%S')) + '\n\n')
                            isBuing = False
                            break  # terminate loop -isBuing-

# !!!!!!!!!!!!!!!!!!!!!! BUY LIMIT with TIMER if fast fall last candel !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    if ((isDn or isBigDn) and cnf.isLMT_GL) or (buy_order and cnf.isLMT_GL):  # if Short trend or started from HSTREmulate and Limit
                        #need_priceLMT = round(cprice - cnf.nLMTautoDnLng_GL,2)
                        if cnf.nLMT_GL_CheckB == 0:
                            need_priceLMT = round(cprice - cnf.nLMT_GL, 2)
                        else:
                            need_priceLMT = round(cprice - cnf.nLMTautoDnLng_GL,2)
                        print('taTradeShTrend()... cnf.nLMT_GL_CheckB: ' + str(cnf.nLMT_GL_CheckB) + '; cnf.nLMT_auto: ' + str(cnf.nLMTautoDnLng_GL) + '; cnf.nLMT_MrgGL: ' + str(cnf.nLMT_GL))
                        if not buy_order:  # if is not order buy yet
                            new_order = newOrderM(pair_name_=bpname, got_qty_=bmyamount, CURR_LIMITS_=CURR_LIMITS, need_cost_=need_priceLMT, side_='BUY', type_='LIMIT', mode='trade')
                            db.add_new_order_buy_appTA_ShTr(cursor, conn, bpname, new_order['orderId'], bmyamount, need_priceLMT, bprofitmarkup, bstoploss, bsellLMT,'limit')  # -10- ??????????
                            if 'orderId' in new_order and cnf.longSQLiteGlb: # check if Create order and Write to data base
                                w3th_scrol.insert(tk.END, 'buy(App)... CREATED! ShortTrend LIMIT; ' + str(bpname) + '\nPrice -> ' + str(need_priceLMT) + '; Amount -> ' + str(bmyamount) + '; ' + str(dt.fromtimestamp(int(time.time()))) +
                                                  '; cnf.bigDnPercent: ' + str(cnf.bigDnPercent)+ '; cnf.nLMTautoDnLng_GL: ' + str(cnf.nLMTautoDnLng_GL)+'\n')
                                new_orderId = new_order['orderId']
                                #w3th_scrol.insert(tk.END, 'Buy(App)... test new_orderId: ' + str(type(new_orderId) + str(new_orderId)) + '\n')
                                dtSB = int(time.time())
                                print('buy(App)... CREATED ShortTrend -LIMIT- '  + str(dt.now().strftime('%H:%M:%S')) + '\n')
                            else:
                                w3th_scrol.insert(tk.END, 'Buy(App)... CREATED and write FALSE! ' + str(dt.now().strftime('%H:%M:%S')) + '\n\n')
                                cnf.App_freezLong_GL = False  # Exit from function
                                isBuing = False
                                break
                        else:
                            new_orderId = str(buy_order[0])
                            w3th_scrol.insert(tk.END, 'Buy(App)... Created Order from DB! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                            dtSB = int(time.time())
                        if new_orderId:
                            while order_statusB:
                                bprice = round(float(cnf.bot.tickerPrice(symbol=cnf.symbolPairGL)['price']), 2)
                                w2th_scrol.delete(0.1, tk.END)
                                bpname, bmyamount, bsellLMT, bprofitmarkup, bstoploss, spendsum, CURR_LIMITS, bdt = BUY(bprice)  # -9-
                                order_status, time_passedS, time_passedM = OrderInfo(bpname,new_orderId,dtSB)
                                if order_status == 'FILLED':
                                    db.update_buy_rate_appTA_ShTr(cursor, conn, new_orderId, need_priceLMT)
                                    w3th_scrol.insert(tk.END, '........... COMPLETE! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                    isBuing = False
                                    break
                                if order_status == 'NEW':
                                    w2th_scrol.insert(tk.END,'buy(App)...ShortTrend -LIMIT- Status NEW \nCurrent rate-> ' + str(bprice) + '\nAim         -> ' + str(need_priceLMT) + '\n..... time passed min. ' + str(time_passedM) + '\n')
                                    print('buy(App)...ShortTrend -LIMIT- Status NEW; Current rate-> ' + str(bprice) + '; Aim-> ' + str(need_priceLMT) + '\n..... time passed min. ' + str(time_passedM) + '\n')
                                    if time_passedM > cnf.BUYlng_LIFE_TIME_MIN and order_status != 'PARTIALLY_FILLED':
                                        cancelL = cnf.bot.cancelOrder(symbol=bpname, orderId=new_orderId)
                                        time.sleep(2)
                                        db.update_buy_Cancel_appTA_ShTr(cursor, conn, new_orderId)
                                        if ('orderId' in cancelL) and cnf.longSQLiteGlb:

                                            w3th_scrol.insert(tk.END,'Buy(App)... Order Cancel SUCCESSFULLY! orderID: ' + str(cancelL['orderId']) + str('; ') + str(dt.now().strftime('%H:%M:%S')) + '\n\n')
                                            print('Buy(App)... Order Cancel SUCCESSFULLY! orderID: ' + str(cancelL['orderId']) + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                            cnf.App_freezLong_GL = False  # Exit from function
                                            isBuing = False
                                            break
                                        else:
                                            w3th_scrol.insert(tk.END, 'Buy(App)... ShortTrend -LIMIT- Cancel order Failed! order: ' + str(cancelL))
                                            print('Buy(App)... ShortTrend -LIMIT- Cancel order Failed! order: ' + str(cancelL)+ '\n')
                                            #msg.showinfo("taTradeShTrend",'Buy(App)... ShortTrend Failed Cancel order or Write DB!')
                                            isBuing = False
                                            #cnf.loop_AppWrkShTr = cnf.loopGL + 1  # Exit from function
                                            break
                                    #w2th_scrol.insert(tk.END, 'buy(App)...ShortTrend -LIMIT- Status is ->  ' + str(order_status) + '; dt -> ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                if order_status == 'PARTIALLY_FILLED':
                                    w2th_scrol.insert(tk.END, 'buy(App)... ShortTrend -LIMIT- status i PARTIALLY_FILLED ' + '\n..... time passed min. ' + str(time_passedM) + '; dt -> ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                if order_status == 'CANCELED':
                                    db.update_buy_Cancel_appTA_ShTr(cursor, conn, new_orderId)
                                    w2th_scrol.insert(tk.END, 'buy(App)... ShortTrend -LIMIT- Status is -> CANCELED ' + '; dt -> ' + str(dt.fromtimestamp(int(time.time()))) + '\n')
                                    cnf.App_freezLong_GL = False  # Exit from function
                                    isBuing = False
                                    break
                                #w2th_scrol.insert(tk.END, 'buy(App)... ShortTrend -LIMIT- Status is ->  ' + str(order_status) + '; time passed -> ' + str(time_passedM) +str(' min.') + '\n')
                                time.sleep(6)  # 6sec
                                #isBuing = False
                        else:
                            w3th_scrol.insert(tk.END, 'Buy(App)... ShortTrend -LIMIT- create new_order Failed!!!  ' + str(dt.now().strftime('%H:%M:%S')) + '\n\n')
                            #isBuing = False
                            break

                    if not isBuing: break  # Exit from loop isBuing
                    thread = threading.Thread(target=run_progressbar(pb00_, cnf.chVarDelay_GL))
                    thread.start()
            if cnf.loop_AppWrkShTr >= cnf.loopGL:
                w2th_scrol.insert(tk.END, 'taTradeShTrend TERMINATE! Loop = ' + str(cnf.loop_AppWrkShTr) +'; '+ str(dt.now().strftime('%H:%M:%S'))+ '\n')
                cnf.App_freezLong_GL = False
        except Exception as e:
            print("ERROR taTradeShTrend().... from WHILE cnf.loop_AppWrkShTr {}".format(e))
            cursor.close()
            time.sleep(10)
            cursor = conn.cursor()
            print('taTradeShTrend()... exception!!!!!!!!!! conn: ' + str(conn) + '; cursor: ' + str(cursor))
            continue
    w2th_scrol.insert(tk.END, 'taTradeShTrend TERMINATE! End Function! loop_AppWrkShTr = ' + str(cnf.loop_AppWrkShTr) + '; ' + str(dt.now().strftime('%H:%M:%S'))+ '\n')
    cursor.close()

def BUY(price):
    # Если остались пары, по которым нет текущих торгов
    if cnf.pairsGL:
        for pair_name, pair_obj in cnf.pairsGL.items():
            try:
                if balances[pair_obj['base']] >= pair_obj['spend_sum']:
                    print("BUY()... balances there is {}".format(balances[pair_obj['base']] ))
                else:
                    print("BUY()... balances is not enough !!! {}".format(balances[pair_obj['base']]))
                    break

                for elem in limits['symbols']:
                    if elem['symbol'] == cnf.symbolPairGL:
                        CURR_LIMITS = elem
                        break
                else:
                    raise Exception("Buy()... Не удалось найти настройки выбранной пары " + cnf.symbolPairGL)
                #price = float(cnf.bot.tickerPrice(symbol=pair_name)['price'])

                # Рассчитываем кол-во, которое можно купить на заданную сумму, и приводим его к кратному значению
                my_amount = adjust_to_step(pair_obj['spend_sum'] / price, CURR_LIMITS['filters'][2]['stepSize'])
                # Если в итоге получается объем торгов меньше минимально разрешенного, то ругаемся и не создаем ордер
                if my_amount < float(CURR_LIMITS['filters'][2]['stepSize']) or my_amount < float(CURR_LIMITS['filters'][2]['minQty']):
                    print("Покупка невозможна, выход. Увеличьте размер ставки")
                    continue

                # Итоговый размер лота
                trade_am = price * my_amount
                # Если итоговый размер лота меньше минимального разрешенного, то ругаемся и не создаем ордер
                if trade_am < float(CURR_LIMITS['filters'][3]['minNotional']):
                    raise Exception("""
                        Buy() Итоговый размер сделки {trade_am:0.8f} меньше допустимого по паре {min_am:0.8f}.
                        Увеличьте сумму торгов (в {incr} раз(а))""".format(
                        trade_am=trade_am, min_am=float(CURR_LIMITS['filters'][3]['minNotional']),
                        incr=float(CURR_LIMITS['filters'][3]['minNotional']) / trade_am
                    ))
                print('Buy()... Рассчитан ордер: кол-во {amount:0.8f}, примерный курс: {rate:0.8f}'.format(amount=my_amount, rate=price))
                sellLMT = adjust_to_step(price * (1 + pair_obj['profit_markup'] / 100 + 0.0015),CURR_LIMITS['filters'][0]['tickSize'])
                # sellLMT = top_price * (1 + pair_obj['profit_markup']/100 + 0.0015)#!!!!!!!!!! temp value for limit sell

                return pair_name, my_amount, sellLMT, pair_obj['profit_markup'], pair_obj['stop_loss'],pair_obj['spend_sum'],CURR_LIMITS,int(time.time())
            except Exception as e:
                print("Error from BUY()... in AppWork {}".format(e))
    else:
        print("Error from BUY()... init variable (press button Init)!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

def SELL(orders_info,curr_rate):
    try:
       isBub = False
       for order, value in orders_info.items():
           pname = value['order_pair']
           print('Sell()...  orders_info {o}'.format(o=orders_info))
           # смотрим, какие ограничения есть для создания ордера на продажу
           for elem in limits['symbols']:
               if elem['symbol'] == pname:
                   CURR_LIMITS = elem
                   break
           else:
               raise Exception("Не удалось найти настройки выбранной пары!!!!!! " + pname)

           if value['panic_fee'] > 0:
               fsell_price = round(value['buy_price'] * (100 - value['panic_fee']-0.15) / 100,2)
           else:
               fsell_price = 0

           got_qty = adjust_to_step(value['buy_amount'], CURR_LIMITS['filters'][2]['stepSize'])
           profit_markup = cnf.pairsGL[pname]['profit_markup']
           #curr_rate = round(float(cnf.bot.tickerPrice(symbol=pname)['price']),2)

           incomeV = round((got_qty * curr_rate) * (1 - 0.00075) - (got_qty * float(value['buy_price'])) * (1 - 0.00075),4)  # commission 0.075%
           incomeP = round((curr_rate / value['buy_price'] - 1)* 100, 2)

           #price_change = ((curr_rate / value['buy_price'] * (1 + 0.0015)) - 1) * 100 # in percent %

           sell = value['buy_price'] * (1 + profit_markup/100 + 0.0015)
           bub = value['buy_price'] * (1 + 0.0015)
           print("SELL()... BUB IS ------------> {}".format(bub))
           if curr_rate > bub:
               isBub = True
           buyDate = dt.strptime(value['buy_created'],'%Y-%m-%d %H:%M:%S')  # преобразует строку в datetime; timestamp() - возвращает время в секундах с начала эпохи.
           buyDateSec = buyDate.timestamp()
           sell_price = adjust_to_step(sell, CURR_LIMITS['filters'][0]['tickSize'])

           return value['order_type'],value['buy_verified'],value['buy_price'], sell_price, fsell_price, order, value['sell_order_id'], got_qty, incomeV,incomeP, profit_markup, value['panic_fee'],pname, CURR_LIMITS, buyDateSec, isBub

    except Exception as e:
        print("Error from SELL()... in AppWork {}".format(e))

def OrderInfo(name,ordID,dti):
    order_status, time_passedSec, time_passedMin = 0,0,0
    try:
        stock_order_data = client.get_order(symbol=name, orderId=ordID)  # , recvWindow=10000)
        order_status = str(stock_order_data['status'])
        #print('OrderInfo()... stock_order_data-> ' + str(stock_order_data))
        #print('OrderInfo()... order Time fromtimestamp-> ' + str(dt.fromtimestamp(round(stock_order_data['time']/1000))))
        #print('OrderInfo()... local time fromtimestamp-> ' + str(dt.fromtimestamp(int(time.time()))))
        time_passedSec = int(time.time()) - dti
        time_passedMin = round(time_passedSec / 60, 2)
    except Exception as e:
        print("Error Error Error from OrderInfo()- {}".format(e))

    return order_status, time_passedSec, time_passedMin

@thread
def portfolio(portf_1th_scrol3_p31_1):
    assetsArray = cnf.client.get_account()
    total = 0
    portf_1th_scrol3_p31_1.delete(0.1, tk.END)
    for item in assetsArray['balances']:
        if float(item.get('free')) > 0:
            #Печат строки кот

            portf_1th_scrol3_p31_1.insert(tk.END, str(item).replace("{", "").replace("asset", "").replace("'", "").replace("}", "")[2:19] + ' USDT' + '\n')
            portf_1th_scrol3_p31_1.insert(tk.END, "********************************************" + '\n')
            if str(item.get('asset')) != 'USDT':

               p = cnf.client.get_symbol_ticker(symbol=str(item.get('asset')) + 'USDT')   # за пару XXXX + USDT
               total += (float(item.get('free')) + float(item.get('locked'))) * float(p['price'])
               portf_1th_scrol3_p31_1.insert(tk.END, "                TOTAL = " + str(total)[0:7] + '\n')
               portf_1th_scrol3_p31_1.insert(tk.END, "********************************************"+ '\n')
            else:
               total += float(item.get('free'))

    portf_1th_scrol3_p31_1.insert(tk.END,  "total Balance = " + str(total)[0:7] + '\n')

# Pressed button Select profit real
def portfolioProf(prof_2th_scrol3_p31_1, flag_):
    conn = sqlite3.connect('binance_app088.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    sum_pv,sum_pp = 0,0

    i,ii,i3,i4 = 0,0,0,0
    sum_pv_sh,sum_pp_sh = 0,0

    inc = 16  # income - table ordersTA
    prf = 17  # profit - table ordersTA
    inc2 = 16  # income - table ordersMRG
    prf2 = 17  # profit - table ordersMRG
    incShTr = 16  # income - table ordersTaShTr
    prfShTr = 17  # profit - table ordersTaShTr
    incMrgShTr = 17  # income - table ordersMRGShTr
    prfMrgShTr = 18  # profit - table ordersMRGShTr

    prof_2th_scrol3_p31_1.delete(0.1, tk.END)
    if flag_ == 1: # if pressed button Select real trade
        get_rec, get_recShort, get_recShTr, get_recMrgShTr  = db.get_rec_ordersTa(cursor, cnf.wdays, 1)

    else: # if pressed button Select emulating trade
        get_rec, get_recShort, get_recShTr, get_recMrgShTr = db.get_rec_ordersTa(cursor,cnf.wdays,0)
        inc = 17
        prf = 20
        inc2 = 14
        prf2 = 17

    for rec in get_rec: # loop in selected Lint
        sum_pv += rec[inc]
        sum_pp += rec[prf]
        i += 1
        #print('get_rec ', rec[16])
    for rec in get_recShort: # loop in selected Lint
        sum_pv_sh += rec[inc2]
        sum_pp_sh += rec[prf2]
        ii += 1
        #print('get_recShort ', rec[16])
    for rec in get_recShTr: # loop in selected
        sum_pv += rec[incShTr]
        sum_pp += rec[prfShTr]
        i3 += 1
    for rec in get_recMrgShTr:  # loop in selected
        sum_pv_sh += rec[incMrgShTr]
        sum_pp_sh += rec[prfMrgShTr]
        i4 += 1
    #print('get_recShTr ', rec[16])

    mess = 'Selected from real trade!' if flag_ == 1 else 'Selected from emulating trade!'
    prof_2th_scrol3_p31_1.insert(tk.END, mess + '\n')
    prof_2th_scrol3_p31_1.insert(tk.END, 'LONG: \nCount trade total: ' + str(i+i3) + '\nTotal profit(in USDT): ' + str(sum_pv)[0:4] + '\nTotal in persent: '+ str(sum_pp)[0:4] +'%' + '\n')
    prof_2th_scrol3_p31_1.insert(tk.END, '----------------------------------------------------' + '\n')
    prof_2th_scrol3_p31_1.insert(tk.END, 'Count trade(SHORT): ' + str(ii+i4) + '\n' + 'Total profit(in USDT-SHORT): ' + str(sum_pv_sh)[0:4] + '\n' + 'Total in persent(SHORT): '+ str(sum_pp_sh)[0:4] +'%' + '\n')
    prof_2th_scrol3_p31_1.insert(tk.END, '----------------------------------------------------' + '\n')
    prof_2th_scrol3_p31_1.insert(tk.END, 'Count Total: ' + str(ii+i+i3+i4) + '\n' + 'Total Profit: ' + str(sum_pv_sh+sum_pv)[0:4] + '\n' + 'Total in persent: '+ str(sum_pp_sh+sum_pp)[0:4] +'%' + '\n')

    cursor.close()

def updatePortfolio():
    conn = sqlite3.connect('binance_app088.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    free_ = 0
    assetsArray = cnf.client.get_account()
    total = 0
    #dt = dt.fromtimestamp(int(time.time()))
    dtnow = dt.now().strftime('%m-%d-%Y')
    for item in assetsArray['balances']:
        if item['asset'] == 'USDT':  free_= float(item["free"])
        if float(item.get('free')) > 0:
            # portf_1th_scrol3_p31_1.insert(tk.END, str(item).replace("{", "").replace("asset", "").replace("'", "").replace("}", "")[2:19] + ' USDT' + '\n')
            # portf_1th_scrol3_p31_1.insert(tk.END, "********************************************" + '\n')
            if str(item.get('asset')) != 'USDT':

                if str(item.get('asset')) != 'RUB':
                    p = cnf.client.get_symbol_ticker(symbol=str(item.get('asset')) + 'USDT')  # рыночная стоимость за пару XXXX + USDT
                    total += (float(item.get('free')) + float(item.get('locked'))) * float(p['price'])
                    # portf_1th_scrol3_p31_1.insert(tk.END, "total = " + str(total)[0:7] + '\n')
                    # portf_1th_scrol3_p31_1.insert(tk.END, "********************************************"+ '\n')
            else:
               total += float(item.get('free'))
    rec_portf = db.get_rec_portfolio(cursor)
    if dtnow == rec_portf[0]: add_rec = 'already add record' # print('already add record')
    else:
        db.add_record_portfolio(cursor,conn,dtnow,total,free_)

    cursor.close()

def select4Tables(hours,countTrades):
    # hours - time frame for select; countTrades -  how many positive trades in sequence
    conn = sqlite3.connect('binance_app088.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    valueNegUp, valueNegDn = [0,0], [0,0]
    valuePosUp, valuePosDn = [0,0],[0,0]
    valuePos = [0,0,0,0]
    #cnf.sum_NegTrades_Gl[1] = 0
    cnf.sum_NegTradesUp_Gl[1] = 0
    cnf.sum_NegTradesDn_Gl[1] = 0

    cnf.sum_PosTrades_Gl[1] = 0 # for sum values

    isTradesPos = False # if there are positive trades in the sequence, and there is none negative

    ordersTA,ordersMrg,ordersTAShTr,ordersMrgShTr = db.get_rec_4Tables(cursor,hours)
    for item in ordersTA: # Select negative income in ordersTA table
        if item[16] < 0:
            valueNegUp[0] += 1
            cnf.sum_NegTradesUp_Gl[1] += round(item[16],2) # sum negative values
        else:
            valuePosUp[0] += 1
            valuePos[0] += 1
            cnf.sum_PosTrades_Gl[1] += round(item[16],2) # sum negative values

    for item in ordersMrg: # Select negative income in ordersMrg table
        if item[16] < 0:
            valueNegDn[0] += 1
            cnf.sum_NegTradesDn_Gl[1] += round(item[16],2) # sum negative values
        else:
            valuePosDn[0] += 1
            valuePos[1] += 1
            cnf.sum_PosTrades_Gl[1] += round(item[16],2) # sum negative values

    for item in ordersTAShTr: # Select negative income in ordersTAShTr table
        if item[16] < 0:
            valueNegUp[1] += 1
            cnf.sum_NegTradesUp_Gl[1] += round(item[16],2) # sum negative values
        else:
            valuePosUp[0] += 1
            valuePos[2] += 1
            cnf.sum_PosTrades_Gl[1] += round(item[16],2) # sum negative values
    cnf.sum_NegTradesDn_Gl[0]
    for item in ordersMrgShTr:# Select negative income in ordersMrgShTr table
        if item[17] < 0:
            valueNegDn[1] += 1
            cnf.sum_NegTradesDn_Gl[1] += round(item[17],2) # sum negative values
        else:
            valuePosDn[1] += 1
            valuePos[3] += 1
            cnf.sum_PosTrades_Gl[1] += round(item[17],2) # sum negative values

    #cnf.sum_NegTrades_Gl[0] = round(sum([v for v in valueNeg]),2)
    cnf.sum_NegTradesUp_Gl[0] = round(sum([v for v in valueNegUp]),2)
    cnf.sum_NegTradesDn_Gl[0] = round(sum([v for v in valueNegDn]),2)
    #print('select4Tables() \nvaluePosUp-> ' + str(valuePosUp) + '\nvaluePosDn-> ' + str(valuePosDn) + '\n')
    #print('select4Tables() \nvalueNegUp-> ' + str(valueNegUp) + '\nvalueNegDn-> ' + str(valueNegDn) + '\n')
    #print('select4Tables(): \ncnf.sum_NegTradesUp_Gl[0]-> ' +str(cnf.sum_NegTradesUp_Gl[0]) + '\ncnf.sum_NegTradesDn_Gl[0]-> ' +str(cnf.sum_NegTradesDn_Gl[0]))

    cnf.sum_PosTrades_Gl[0] = round(sum([v for v in valuePos]),2) # for sum items
    #print('select4Tables() cnf.sum_PosTrades_Gl[0]-> ' + str(cnf.sum_PosTrades_Gl[0]) + '; cnf.sum_PosTrades_Gl[1]-> ' + str(cnf.sum_PosTrades_Gl[1]) + '\n')

    if (cnf.sum_NegTradesUp_Gl[0] == 0) and (cnf.sum_NegTradesDn_Gl[0] == 0) and (cnf.sum_PosTrades_Gl[0] >= countTrades):
        isTradesPos = True

    cursor.close()

    return isTradesPos

def firstInitDB():
    conn = sqlite3.connect('binance_app088.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    db.make_initial_tables_appTA(cursor)  # table for MACD alg
    db.make_initial_tables_appTA_ShTr(cursor)  # table for Short Trend alg
    db.make_initial_table_MRG(cursor)  # _taTrade
    db.make_initial_table_MRG_ShTr(cursor)
    db.make_initial_tables_emTA(cursor) # Emulation table for MACD alg
    db.make_initial_emTA_ShTr(cursor) # Emulation table forShort Trendalg
    db.make_initial_table_emMRG(cursor)
    db.make_initial_table_emMRG_ShTr(cursor)
    cursor.close()


