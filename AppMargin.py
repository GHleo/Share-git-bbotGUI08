import tkinter as tk
from datetime import datetime as dt
from tkinter import messagebox as msg
import time
import sqlite3
import threading
import random
from binance.client import Client
import configGlb as cnf
import ta as ta
import keys
import queriesToDB as db
from misc import adjust_to_step, MA_Cross, macdCross, newOrderM, macdSignalCross

limits = cnf.bot.exchangeInfo()  # Получаем лимиты пары с биржи
client = Client(keys.apikey, keys.apisecret)

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
def mrgTradeMACD(m1th_scrol, m4th_scrol,m5th_scrol,pb00_):
    conn = sqlite3.connect('binance_app088.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    db.make_initial_table_MRG(cursor)  # _taTrade
    global isBuing, isSelling
    isSelling, isBuing = True, True  # for loop buy
    cnf.shortSQLiteGlb, cnf.shortSQLiteGlbBuy = False, False #flag for approve transaction
    #balancesBTC = {info['asset']: float(info['free']) for info in cnf.bot.marginAccount()['userAssets'] if info['asset'] == 'BTC'}
    m4th_scrol.delete(0.1, tk.END)
    m5th_scrol.delete(0.1, tk.END)
    m5th_scrol.insert(tk.END,'mrgTradeMACD() -> START!!!'+ '\n')
    while cnf.loop_AppMrgMACD < cnf.loopMrgGL and cnf.AppMrg_freezShort_GL:
        try:
            cnf.isWork_or_Mrg = False  # for take on AppMargin
            order_statusS, order_statusB = True, True
            new_orderId,dtSB = 0, 0
            db.get_open_orders_MRG(cursor)
            sell_order = [order for order in cnf.orders_infoMrgMACD] # sell_order_id for limit sell
            print('************ mrgTradeMACD sell_order: ' + str(sell_order))
# !!!!!!!!!!!!!!!!! BUY BUY BUY !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            if cnf.orders_infoMrgMACD and not isSelling:
                cnf.isWork_or_Mrg = True  # for take on AppMargin
                delay_ = 0.05
                while isBuing:
                    bprice = round(float(cnf.bot.tickerPrice(symbol=cnf.symbolPairGL)['price']), 2)
                    print('Buy(Mrg)... MACD While isBuing! ' + str(dt.now().strftime('%H:%M:%S'))+ '\n')
                    btype, pname, sorder, buyorder, sgotqty, sellprice, needcost, fprice, sverified, sloss, incomeV,incomeP, profit, CURR_LIMITS, sdtSec, isBub = BUY(cnf.orders_infoMrgMACD,bprice)  # -14-
                    if sverified and btype == 'sell':
                        time_passedM = round((int(time.time()) - sdtSec) / 60, 2)
                        m4th_scrol.delete(0.1, tk.END)
                        m4th_scrol.insert(tk.END, 'Buy(Mrg)... MACD; Profit/SLoss -> ' + str(profit) + '/' + str(sloss) + '\n' + 'Sold      -> ' + str(sellprice) + '\n'+ 'Curr rate         -> '
                            + str(bprice) + '\n' + 'Aim price -> ' + str(needcost) + '\n' + 'Forc sell -> ' + str(fprice) + '\n' + 'Income(%) -> ' + str(incomeP)+'\n'+str(cnf.BUYshrt_LIFE_TIME_MIN)+' min. limit; ..... time passed min. ' + str(time_passedM) + '\n')
# !!!!!!!!!!!!!!!!!!!!!! BUY MARKET with STOP LOSS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                        if cnf.isMRKT_GL:
                            if time_passedM > cnf.BUYshrt_LIFE_TIME_MIN and isBub: #if time limit over
                                new_order = newOrderM(pair_name_=pname, got_qty_=sgotqty, CURR_LIMITS_=CURR_LIMITS,need_cost_=0, side_='BUY', type_='MARKET', mode='short')
                                db.store_buy_order_MRG(cursor, conn, new_order['orderId'], sorder, sgotqty)
                                buystatus, time_passedS, time_passedM, iprice = OrderInfo(pname, new_order['orderId'], sdtSec)
                                if 'orderId' in new_order:
                                    if buystatus == 'FILLED':
                                        db.update_buy_order_MRG(cursor, conn, sorder, bprice, incomeV,1)  # sorder is buy_order_id
                                        m5th_scrol.insert(tk.END, 'BuyBUB... Price-> ' + str(bprice) + '; Income($)-> ' + str(incomeV) + '; ' +  str(dt.now().strftime('%H:%M:%S')) + '\n\n')
                                        cnf.loop_AppMrgMACD += 1
                                        cnf.AppMrg_freezShort_GL = False
                                        break
                                else:
                                    m5th_scrol.insert(tk.END,'Buy(Mrg)Bub... new_order Failed!!! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                    cnf.loop_AppMrgMACD = cnf.loopMrgGL + 1
                                    break
                            if bprice <= needcost:
                                new_order = newOrderM(pair_name_=pname, got_qty_=sgotqty, CURR_LIMITS_=CURR_LIMITS,need_cost_=0, side_='BUY', type_='MARKET', mode='short')
                                db.store_buy_order_MRG(cursor, conn, new_order['orderId'], sorder, sgotqty)
                                buystatus, time_passedS, time_passedM, iprice = OrderInfo(pname, new_order['orderId'], sdtSec)
                                if 'orderId' in new_order:
                                    if buystatus == 'FILLED':
                                        db.update_buy_order_MRG(cursor, conn, sorder,bprice , incomeV,1)  # sorder is buy_order_id
                                        m5th_scrol.insert(tk.END, 'Buy(Mrg)... Price-> ' + str(bprice) + '; Income($)-> ' + str(incomeV) + '; ' +  str(dt.now().strftime('%H:%M:%S')) + '\n\n')
                                        cnf.loop_AppMrgMACD += 1
                                        cnf.AppMrg_freezShort_GL = False
                                        break
                                else:
                                    m5th_scrol.insert(tk.END,'Buy(Mrg)... new_order Failed!!! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                    cnf.loop_AppMrgMACD = cnf.loopMrgGL + 1
                                    break
                            if (fprice < bprice) and (sloss > 0):
                                new_orderF = newOrderM(pair_name_=pname, got_qty_=sgotqty, CURR_LIMITS_=CURR_LIMITS,need_cost_=0, side_='BUY', type_='MARKET', mode='short')
                                time.sleep(1)  # 1 sec
                                db.store_buy_order_MRG(cursor, conn, new_orderF['orderId'], sorder, sgotqty)
                                buystatus, time_passedS, time_passedM, iprice = OrderInfo(pname, new_orderF['orderId'], sdtSec)
                                if 'orderId' in new_orderF:
                                    if buystatus == 'FILLED':
                                        db.update_buy_order_MRG(cursor, conn, sorder, bprice, incomeV,0)  # sorder is buy_order_id
                                        m5th_scrol.insert(tk.END,'Buy(Mrg)... Force Sell Price-> ' + str(bprice) + '; Income($)-> ' + str(incomeV) + '; '  +  str(dt.now().strftime('%H:%M:%S'))+ '\n\n')
                                        cnf.loop_AppMrgMACD += 1
                                        cnf.AppMrg_freezShort_GL = False
                                        break
                                else:
                                    m5th_scrol.insert(tk.END,'Force Buy(Mrg)... new_order Failed!!! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                    cnf.loop_AppMrgMACD = cnf.loopMrgGL + 1
                                    break
# !!!!!!!!!!!!!!!!!!!!!! BUY LIMIT with STOP LOSS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                        if cnf.isLMT_GL:
                            #db.get_open_orders_MRG(cursor)
                            btype, pname, sorder, buyorder, sgotqty, sellprice, needcost, fprice, sverified, sloss, incomeV,incomeP, profit, CURR_LIMITS, sdtSec, isBub = BUY(cnf.orders_infoMrgMACD,bprice)  # -14-
# ---------------------- Check created sell order (there is in table) or not
                            if not buyorder:  # create first buy order
                                new_order = newOrderM(pair_name_=pname, got_qty_=sgotqty, CURR_LIMITS_=CURR_LIMITS,need_cost_=needcost, side_='BUY', type_='LIMIT', mode='short')
                                db.store_buy_order_MRG(cursor, conn, new_order['orderId'], sorder, sgotqty)
                                if 'orderId' in new_order and cnf.shortSQLiteGlbBuy: # check if Create order and Write to data base
                                    new_orderId = new_order['orderId']  # orderID
                                    m5th_scrol.insert(tk.END, 'Buy(Mrg)... CREATE -LIMIT- ' + str(dt.now().strftime('%H:%M:%S')) + '\n' + 'Need Price-> ' + str(needcost) + '\n')
                                    print("Buy(Mrg)... -LIMIT- new_order {no}; buy order {cn}".format(no=new_orderId, cn=sorder))
                                    dtSB = int(time.time())
                                else:
                                    m5th_scrol.insert(tk.END, 'Buy(Mrg)... Create and write FALSE! cnf.longSQLiteGlbBuy = ' + str(cnf.shortSQLiteGlbBuy) +'; ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                    msg.showinfo("mrgTradeMACD", 'Buy(Mrg)... Some problem when creating a new order!')
                            else:
                                new_orderId = buyorder
                                m5th_scrol.insert(tk.END, 'Buy(Mrg)...  Created order from DB! ' + str(dt.now().strftime('%H:%M:%S')) + '\n') # + 'Need Price-> ' + str(needcost) + '\n')
                                dtSB = int(time.time())
                            print('Buy(Mrg)...  MACD -isBuing- sorder: ' + str(sorder) + '; buyorder: ' + str(buyorder)+ '; new_orderSL: ' + str(new_orderId))
                            if new_orderId:
                                isForce = 1 # if 1 - not force sell else force sell
                                while order_statusB:
                                    blprice = round(float(cnf.bot.tickerPrice(symbol=cnf.symbolPairGL)['price']), 2)
                                    m4th_scrol.delete(0.1, tk.END)
                                    btype, pname, sorder, buyorder, sgotqty, sellprice, needcost, fprice, sverified, sloss, incomeV,incomeP, profit, CURR_LIMITS, sdtSec, isBub = BUY(cnf.orders_infoMrgMACD,blprice)  # -14-
                                    buystatus, time_passedS, time_passedM, iprice = OrderInfo(pname, new_orderId, dtSB)
                                    print("Buy(Mrg)... MACD -LIMIT(while order_statusS)- Order status  {os};".format(os=buystatus))
                                    if buystatus == 'FILLED':
                                        db.update_buy_order_MRG(cursor, conn, sorder, blprice, incomeV, isForce)
                                        if cnf.shortSQLiteGlbBuy:
                                            m5th_scrol.insert(tk.END, '............ COMPLETE ' + str(dt.fromtimestamp(int(time.time()))) + '\n' + 'Income($)-> ' + str(incomeV) + ' Time passed min. -> ' + str(time_passedM) + '\n\n')
                                        else:
                                            msg.showinfo("mrgTradeMACD",'Buy... Some problem when write to DB!')
                                        cnf.loop_AppMrgMACD += 1
                                        isBuing = False # for exit from top loop iBuingg
                                        cnf.AppMrg_freezShort_GL = False
                                        break
                                    if buystatus == 'NEW':
                                        print('Buy.. MACD -LIMIT- order_status  {os}; datetime {dt}; time passed {tp} min.'.format(os=buystatus, dt=dt.fromtimestamp(int(time.time())), tp=time_passedM))
                                        m4th_scrol.insert(tk.END,'Buy.. MACD -LIMIT-; Profit/SLoss -> ' + str(profit) + '/' + str(sloss) + '\n' + 'Sold      -> ' + str(sellprice) + '\n' + 'Curr rate         -> ' + str(blprice) + '\n'
                                                          + 'Aim price -> ' + str(needcost) + '\n' + 'Forc sell -> ' + str(fprice) + '\n' + 'Income(%) -> ' + str(incomeP) + '\n'+ str(cnf.BUYshrt_LIFE_TIME_MIN)+' min. limit; ..... time passed min. ' + str(time_passedM) + '\n')

                                        if time_passedM > cnf.BUYshrt_LIFE_TIME_MIN and isBub and buystatus != 'PARTIALLY_FILLED':
                                            m4th_scrol.insert(tk.END, 'Time passed ->  ' + str(time_passedM) + ' min. Exit Order: ' + str(new_orderId) + '\n')
                                            cancel = cnf.client.cancel_margin_order(symbol=pname, orderId=new_orderId)
                                            time.sleep(2)
                                            if 'orderId' in cancel:
                                                m5th_scrol.insert(tk.END, 'Buy... Order Cancel SUCCESSFULLY! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                                new_order = newOrderM(pair_name_=pname, got_qty_=sgotqty,CURR_LIMITS_=CURR_LIMITS,need_cost_=0, side_='BUY', type_='MARKET', mode='short')
                                                new_orderId = new_order['orderId']
                                                if new_orderId:
                                                    m5th_scrol.insert(tk.END,'BuyBub... CREATE Market Order. ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                                else:
                                                    m5th_scrol.insert(tk.END,'BuyBub... -LIMIT- new_order Failed!!! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                                    msg.showinfo("mrgTradeMACD",'BuyBub... Some problem when creating a new order!')
                                            else:
                                                m4th_scrol.insert(tk.END, 'Buy(Mrg)... MACD -LIMIT- Order Cancel FAILD!!! ' + str(dt.fromtimestamp(int(time.time()))) + '\n')
                                                msg.showinfo("mrgTradeMACD",'BuyBub... Some problem when cancel order!')
                                    if buystatus == 'PARTIALLY_FILLED':
                                        m5th_scrol.insert(tk.END, 'Buy(Mrg)... MACD -LIMIT- Status is ->  ' + str(buystatus) + '; Current rate -> ' + str(blprice)+ '\n')
                                    if buystatus == 'CANCELED':
                                        m5th_scrol.insert(tk.END,'CANCELED!!! new_orderId:  ' + str(new_orderId) + '; dt -> ' + str(dt.fromtimestamp(int(time.time()))) + '\n\n')
                                        isBuing = False # for exit from top loop iBuingg
                                        cnf.AppMrg_freezShort_GL = False
# ----------------------------- Buy LIMIT when STOP LOSS ----------------------
                                    if fprice < blprice and sloss > 0 and buystatus != 'PARTIALLY_FILLED':
                                        print("Force  Buy(Mrg)... MACD -LIMIT- fprice {sl} - curate {cr}".format(sl=fprice, cr=blprice))
                                        cancelF = cnf.client.cancel_margin_order(symbol=pname, orderId=new_orderId)
                                        time.sleep(2)
                                        if 'orderId' in cancelF:
                                            m5th_scrol.insert(tk.END, 'Force Buy... Order Cancel SUCCESSFULLY! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                            new_orderF = newOrderM(pair_name_=pname, got_qty_=sgotqty,CURR_LIMITS_=CURR_LIMITS, need_cost_=0,side_='BUY', type_='MARKET',mode='short')  # force sell
                                            #db.update_buy_lmt_MRG(cursor, conn, sorder,new_orderF['orderId'])  # ????? UPDATE order_Id(Force buy) same record in store_buy_order_MRG ????
                                            isForce = 0
                                            new_orderId = new_orderF['orderId']
                                            if new_orderId:
                                                m5th_scrol.insert(tk.END, 'Force Buy... CREATE Market Order. ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                            else:
                                                m5th_scrol.insert(tk.END,'Force Buy(Mrg)... -LIMIT- new_order Failed!!! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                                msg.showinfo("mrgTradeMACD",'Force Buy(Mrg)... Some problem when creating a new order!')
                                        else:
                                            m5th_scrol.insert(tk.END,'Force Buy... MACD -LIMIT- Order Cancel FAILD!!! ' + str(dt.fromtimestamp(int(time.time()))) + '\n')
                                            msg.showinfo("mrgTradeMACD",'Force Buy... Some problem when cancel order!')
                                    time.sleep(6)  # 6sec
                            else:
                                m5th_scrol.insert(tk.END, 'Buy(Mrg)... -LIMIT- new_order Failed!!! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                # cnf.loop_AppMrgMACD = cnf.loopMrgGL + 1
                                # break

                        if not isBuing: break  # Exit from loop isBuing
                    else:
                        print('ERROR Buy... MACD - Sell do not accept (not verified) !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ')
                    thread = threading.Thread(target=run_progressbar(pb00_, delay_))
                    thread.start()
# !!!!!!!!!!!!!!!!! SELL SELL SELL !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            else:
                while isSelling and cnf.AppMrg_freezShort_GL:
                    klines = cnf.bot.klines(symbol=cnf.symbolPairGL, interval=cnf.KlineMrgGL, limit=cnf.KLINES_LIMITS)
                    klinesMinusLast = klines[:len(klines) - int(cnf.USE_OPEN_CANDLES)]
                    closes = [float(x[4]) for x in klinesMinusLast]
                    price = round(float(cnf.bot.tickerPrice(symbol=cnf.symbolPairGL)['price']), 2)
                    macd, macdsignal, macdhist = ta.MACD(closes, 7, 14, 9)

                    Ups, Dns = macdSignalCross(macd[-3:], macdsignal[-3:]) #give 3 last value
                    if not cnf.isWork_or_Mrg:
                        m1th_scrol.delete(0.1, tk.END)
                        m1th_scrol.insert(tk.END, '### Working Margin use MACD! (mrgTradeMACD) ###' + '\n' + '      (When selling in progress it freez!) ' + '\n\n')
                        m1th_scrol.insert(tk.END, 'MACD -> EMA Short/Long/Signal -> 7/14/9' + '\n\n' + 'KLINES_LIMITS(period)-> ' + str(cnf.KLINES_LIMITS) + '\n' + 'TIMEFRAME(in minutes)-> ' + str(cnf.KlineMrgGL) + '\n')
                        m1th_scrol.insert(tk.END, 'Sell  LIFE_TIME_MIN -> ' + str(cnf.SELLshrt_LIFE_TIME_MIN) + '\n' + 'Buy LIFE_TIME_MIN   -> ' + str(cnf.BUYshrt_LIFE_TIME_MIN) + '\n')
                        m1th_scrol.insert(tk.END, '------------------------------------------------\n\n'+ str(dt.fromtimestamp(int(time.time()))) + '\n')
                        m1th_scrol.insert(tk.END, 'Is Market/Limit? -> ' + str(cnf.isMRKT_GL) + '/' + str(cnf.isLMT_GL) + '\n' + 'Is cross Down?   -> ' + str(Ups) + '\n' + 'Rate             -> ' + str(price) + '\n')
                        m1th_scrol.insert(tk.END,'------------------------------------------------' + '\n')

                    pname, amount, spendsumMRG, profit, stoploss, CURR_LIMITS, sdt = SELL(price)  # -8-
# !!!!!!!!!!!!!!!!!!!!!! SELL MARKET if fast Grow last candel !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    if Dns and cnf.isMRKT_GL:  # if SHORT TREND or STARTED from HSTREmulate and Market
                        print('Sell(Mrg)... MACD -MARKET-  if Dns {iu} isMRKT_GL  {m}'.format(iu=Dns, m=cnf.isMRKT_GL))
                        new_order = newOrderM(pair_name_=pname, got_qty_=amount, CURR_LIMITS_=CURR_LIMITS, need_cost_=0,side_='SELL', type_='MARKET', mode='short')
                        db.add_new_order_SELL_MRG(cursor, conn, pname, new_order['orderId'], amount, price, spendsumMRG,profit, stoploss, 'market')  # -10-
                        if 'orderId' in new_order:
                            order_status, time_passedS, time_passedM, iprice = OrderInfo(pname, new_order['orderId'],sdt)
                            m5th_scrol.insert(tk.END, 'Sell(Mrg)... CREATE MACD -MARKET- Pair-> ' + str(pname) + '\n' + 'Price-> ' + str(price) + '; Amount: ' + str(amount) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                            if order_status == 'FILLED':
                                db.update_sell_MRG(cursor, conn, new_order['orderId'], price)
                                m5th_scrol.insert(tk.END, '............ COMPLETE!  '+ str(dt.now().strftime('%H:%M:%S')) + '\n')
                                isSelling = False
                                break  # terminate loop -isSelling-
                            else:
                                m5th_scrol.insert(tk.END, 'Create Sell Order do not FILLED!  '+ str(dt.now().strftime('%H:%M:%S')) + '\n')
                                isSelling = False
                                break  # terminate loop -isSelling-
                        else:
                            m5th_scrol.insert(tk.END,'Sell(Mrg)... MAKD -MARKET- orderId is not in new_order!!! ' + str(dt.now().strftime('%H:%M:%S')) + '\n\n')
                            isSelling = False
                            break  # terminate loop -isSelling-
# !!!!!!!!!!!!!!!!!!!!!! SELL LIMIT with TIMER  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    if (Dns and cnf.isLMT_GL) or (sell_order and cnf.isLMT_GL):  # if Short trend or started from HSTREmulate and Limit
                        #need_priceLMT = round(price + cnf.nLMTautoUpMrg_GL,2)  # 5$ buy low on base crypto ????????? we need correcting sellLMT
                        if cnf.nLMT_GL_CheckB == 0:
                            need_priceLMT = round(price - cnf.nLMT_MrgGL, 2)
                        else:
                            need_priceLMT = round(price + cnf.nLMTautoUpMrg_GL,2)
                        print('mrgTradeMACD()... cnf.nLMT_GL_CheckB: ' + str(cnf.nLMT_GL_CheckB) + '; cnf.nLMT_auto: ' + str(cnf.nLMTautoUpMrg_GL) + '; cnf.nLMT_MrgGL: ' + str(cnf.nLMT_MrgGL))
                        if not sell_order:  # create first buy order
                            new_order = newOrderM(pair_name_=pname, got_qty_=amount, CURR_LIMITS_=CURR_LIMITS, need_cost_=need_priceLMT, side_='SELL', type_='LIMIT', mode='short')
                            db.add_new_order_SELL_MRG(cursor, conn, pname, new_order['orderId'], amount, price,spendsumMRG, profit, stoploss, 'market')  # -10-
                            if 'orderId' in new_order and cnf.shortSQLiteGlb: # check if Create order and Write to data base
                                new_orderId = new_order['orderId']
                                m5th_scrol.insert(tk.END, 'Sell(Mrg)... CREATED! MACD LIMIT; ' + str(pname) + '\nPrice-> ' + str(price) + '; Amount: ' + str(amount) + '; ' + str(dt.now().strftime('%H:%M:%S')) +
                                                  '; cnf.nLMTautoUpMrg_GL: ' + str(cnf.nLMTautoUpMrg_GL) + '\n')
                                dtSB = int(time.time())
                            else:
                                m5th_scrol.insert(tk.END, 'Sell(Mrg)... CREATED and write FALSE! ' + str(dt.now().strftime('%H:%M:%S')) + '\n\n')
                                cnf.AppMrg_freezShort_GL = False  # Exit from function
                                isSelling = False
                                break
                        else:
                            new_orderId = str(sell_order[0])
                            m5th_scrol.insert(tk.END, 'Sell(Mrg)... CREATED MACD -LIMIT- Repeated! ' + str(dt.now().strftime('%H:%M:%S')) + '\nNeed Price-> ' + str(need_priceLMT) + '\n')
                            #m5th_scrol.insert(tk.END, 'Sell(Mrg)... test sell_order: ' + str(type(sell_order)) + str(sell_order[0]) + '\n')
                            dtSB = int(time.time())
                        if new_orderId:
                            while order_statusS:
                                sprice = round(float(cnf.bot.tickerPrice(symbol=cnf.symbolPairGL)['price']), 2)
                                m4th_scrol.delete(0.1, tk.END)
                                order_status, time_passedS, time_passedM, iprice = OrderInfo(pname, new_orderId, dtSB )
                                if order_status == 'FILLED':
                                    db.update_sell_MRG(cursor, conn, new_orderId, sprice)
                                    m5th_scrol.insert(tk.END, '............ COMPLETE -> ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                    isSelling = False
                                    break
                                if order_status == 'NEW':
                                    print('Sell(Mrg)... MACD -LIMIT- Status NEW Current rate-> ' + str(sprice) + 'Aim-> ' + str(need_priceLMT) + '\n' + '..... time passed min. ' + str(time_passedM) + '\n')
                                    m4th_scrol.insert(tk.END,'Sell(Mrg)... MACD -LIMIT- \nCurrent rate-> ' + str(sprice) + '\nAim         -> ' + str(need_priceLMT) + '\n' + '..... time passed min. ' + str(time_passedM) + '\n')
                                    if time_passedM > cnf.SELLshrt_LIFE_TIME_MIN and order_status != 'PARTIALLY_FILLED':
                                        print("Sell(Mrg)... MACD -LIMIT- Ордер {order} пора отменять, прошло {passed:0.2f} min.".format(order=new_orderId, passed=time_passedM))
                                        # Отменяем ордер на бирже
                                        cancel = cnf.client.cancel_margin_order(symbol=pname, orderId=new_orderId)
                                        db.update_sell_Cancel_MRG(cursor, conn, new_orderId)
                                        #time.sleep(1)  # 1sec
                                        if ('orderId' in cancel) and cnf.shortSQLiteGlb:
                                            print('Sell(Mrg)... Order Cancel SUCCESSFULLY! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                            m5th_scrol.insert(tk.END,'Sell(Mrg)... Order Cancel SUCCESSFULLY! ' + str(dt.now().strftime('%H:%M:%S')) + '\n\n')
                                            cnf.AppMrg_freezShort_GL = False  # Exit from function
                                            isSelling = False
                                            break
                                        else:
                                            m5th_scrol.insert(tk.END,'Sell(Mrg)... -LIMIT- Cancel order Failed!!!!!!!! order: ' + str(cancel))
                                            print('Sell(Mrg)... -LIMIT- Cancel order Failed!!!!!!!! order: ' + str(cancel))
                                            msg.showinfo("mrgTradeMACD",'Sell(Mrg).... MACD Failed Cancel order or Write DB!')
                                            isSelling = False
                                            break
                                if order_status == 'PARTIALLY_FILLED':
                                    print("Sell(Mrg)... MACD -LIMIT- Ордер {order} частично исполнен, ждем завершения".format(order=new_orderId))
                                    m4th_scrol.insert(tk.END, 'Sell(Mrg)... MACD -LIMIT- status is PARTIALLY_FILLED ' + '\n' + '..... time passed min. ' + str(time_passedM) + '; dt -> ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                if order_status == 'CANCELED':
                                    db.update_sell_Cancel_MRG(cursor, conn, new_orderId)
                                    m4th_scrol.insert(tk.END, 'Sell(Mrg)... MACD -LIMIT- Status is -> CANCELED! ' + str(dt.fromtimestamp(int(time.time()))) + '\n')
                                    cnf.AppMrg_freezShort_GL = False  # Exit from function
                                    isSelling = False
                                    break
                                #m4th_scrol.insert(tk.END, 'Sell(Mrg)... MACD -LIMIT- Status is ->  ' + str(order_status) + '; time passed -> ' + str(time_passedM) +str(' min.\n'))
                                time.sleep(6)  # 6 sec
                        else:
                            m5th_scrol.insert(tk.END, 'Sell(Mrg)... MACD -LIMIT- orderId is not in new_orderL!!!  ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                            isSelling = False
                            break  # terminate loop -isSelling-
                    if not isSelling: break  # Exit from loop isSelling

                    thread = threading.Thread(target=run_progressbar(pb00_, cnf.chVarDelay_GL))
                    thread.start()
            if cnf.loop_AppMrgMACD >= cnf.loopMrgGL:
                m4th_scrol.insert(tk.END, 'mrgTradeMACD TERMINATE! Loop = ' + str(cnf.loop_AppMrgMACD) + '; ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                cnf.AppMrg_freezShort_GL = False
        except Exception as e:
            print("time.sleep(10) ERROR mrgTradeMACD().... from WHILE nf.loop_AppMrgMACD {}".format(e))
            time.sleep(10)
            continue
    m4th_scrol.insert(tk.END, 'mrgTradeMACD TERMINATE - End Function! loop_AppMrgMACD = ' + str(cnf.loop_AppMrgMACD) + '; ' + str(dt.now().strftime('%H:%M:%S'))+ '\n')
    cursor.close()
@thread
def mrgTradeShTr(m1th_scrol, m4th_scrol,m5th_scrol,pb00_):
    conn = sqlite3.connect('binance_app088.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    db.make_initial_table_MRG_ShTr(cursor)
    m4th_scrol.delete(0.1, tk.END)
    m5th_scrol.delete(0.1, tk.END)
    m5th_scrol.insert(tk.END,'mrgTradeShTr -> START!!!'+ '\n')
    isSelling, isBuing = True, True  # for loop buy
    cnf.shortSQLiteGlb, cnf.shortSQLiteGlbBuy = False, False #flag for approve transaction
    #balancesBTC = {info['asset']: float(info['free']) for info in cnf.bot.marginAccount()['userAssets'] if info['asset'] == 'BTC'}
    while cnf.loop_AppMrgShTr < cnf.loopMrgGL and cnf.AppMrg_freezShort_GL:
        try:
            cnf.isWork_or_Mrg_ShTr = False
            new_orderSL, new_orderId, dtSB = 0,0,0
            order_statusS, order_statusB = True,True
            db.get_open_orders_MRG_ShTr(cursor)
            sell_order = [order for order in cnf.orders_infoMrgShTr] # sell_order_id for limit sell
            print('************ mrgTradeShTr sell_order: ' + str(sell_order))
# !!!!!!!!!!!!! BUY BUY BUY !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            if cnf.orders_infoMrgShTr and not isSelling:
                cnf.isWork_or_Mrg_ShTr = True
                delay_ = 0.05
                while isBuing:
                    bprice = round(float(cnf.bot.tickerPrice(symbol=cnf.symbolPairGL)['price']), 2)
                    print('Buy(Mrg)... Short Trend While isBuing! ' + str(dt.now().strftime('%H:%M:%S'))+ '\n')
                    btype, pname,sorder,buyorder, sgotqty, sellprice, needcost, fprice, sverified, sloss, incomeV, incomeP,profit, CURR_LIMITS, sdtSec, isBub = BUY(cnf.orders_infoMrgShTr,bprice) # -14-
                    if sverified and btype == 'sell':
                        time_passedM = round((int(time.time()) - sdtSec) / 60, 2)
                        m4th_scrol.delete(0.1, tk.END)
                        m4th_scrol.insert(tk.END, 'Buy(Mrg)... Short Trend; Profit/StopLoss -> ' + str(profit) + '/' + str(sloss) + '\n' + 'Sold      -> ' + str(sellprice) + '\n' + 'Curr rate         -> ' + str(bprice) +
                                          '\n' + 'Aim price -> ' + str(needcost) + '\n' + 'Forc sell -> ' + str(fprice) + '\n' + 'Income(%) -> ' + str(incomeP) + ' %\n'+ str(cnf.BUYshrt_LIFE_TIME_MIN)+' min. limit; ..... time passed min. ' + str(time_passedM) + '\n')
# !!!!!!!!!!!!!!!!!!!!!! BUY MARKET with TOP LOSS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                        if cnf.isMRKT_GL:
                            if time_passedM > cnf.BUYshrt_LIFE_TIME_MIN and isBub: #if time limit over
                                new_order = newOrderM(pair_name_=pname, got_qty_=sgotqty,CURR_LIMITS_=CURR_LIMITS, need_cost_=0, side_='BUY', type_='MARKET',mode='short')
                                db.store_buy_order_MRG_ShTr(cursor, conn, new_order['orderId'], sorder, sgotqty)
                                buystatus, time_passedS, time_passedM, iprice = OrderInfo(pname, new_order['orderId'], sdtSec)
                                if 'orderId' in new_order:
                                    if buystatus == 'FILLED':
                                        db.update_buy_order_MRG_ShTr(cursor, conn, sorder, bprice, incomeV,1) # sorder is buy_order_id
                                        m5th_scrol.insert(tk.END, 'BuyBub... Price-> ' + str(bprice) + '; Income($)-> ' + str(incomeV) + ' $; ' + str(dt.now().strftime('%H:%M:%S')) + '\n\n')
                                        cnf.loop_AppMrgShTr += 1
                                        cnf.AppMrg_freezShort_GL = False
                                        break
                                    else:
                                        m5th_scrol.insert(tk.END, 'BuyBub... new_order Failed!!! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                        cnf.loop_AppMrgShTr = cnf.loopMrgGL + 1
                                        break
                            if bprice <= needcost:
                                new_order = newOrderM(pair_name_=pname, got_qty_=sgotqty,CURR_LIMITS_=CURR_LIMITS, need_cost_=0, side_='BUY', type_='MARKET',mode='short')
                                db.store_buy_order_MRG_ShTr(cursor, conn, new_order['orderId'], sorder, sgotqty)
                                buystatus, time_passedS, time_passedM, iprice = OrderInfo(pname, new_order['orderId'], sdtSec)
                                if 'orderId' in new_order:
                                    if buystatus == 'FILLED':
                                        db.update_buy_order_MRG_ShTr(cursor, conn, sorder, bprice, incomeV,1) # sorder is buy_order_id
                                        m5th_scrol.insert(tk.END, 'Buy(Mrg)... Price-> ' + str(bprice) + '; Income($)-> ' + str(incomeV) + ' $; ' + str(dt.now().strftime('%H:%M:%S')) + '\n\n')
                                        cnf.loop_AppMrgShTr += 1
                                        cnf.AppMrg_freezShort_GL = False
                                        break
                                    else:
                                        m5th_scrol.insert(tk.END, 'Buy(Mrg)... new_order Failed!!! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                        cnf.loop_AppMrgShTr = cnf.loopMrgGL + 1
                                        break
                            if fprice < bprice and sloss > 0:
                                new_orderF = newOrderM(pair_name_=pname, got_qty_=sgotqty, CURR_LIMITS_=CURR_LIMITS,need_cost_=0, side_='BUY', type_='MARKET', mode='short')
                                db.store_buy_order_MRG_ShTr(cursor, conn, new_orderF['orderId'], sorder, sgotqty)
                                buystatus, time_passedS, time_passedM, iprice = OrderInfo(pname, new_orderF['orderId'], sdtSec)
                                if 'orderId' in new_orderF:
                                    if buystatus == 'FILLED':
                                        db.update_buy_order_MRG_ShTr(cursor, conn, sorder, bprice, incomeV,0) # sorder is buy_order_id
                                        m5th_scrol.insert(tk.END, 'Force Buy Price-> ' + str(bprice) + '; Income($)-> ' + str(incomeV) + ' %; ' + str(dt.now().strftime('%H:%M:%S')) + '\n\n')
                                        cnf.loop_AppMrgShTr += 1
                                        cnf.AppMrg_freezShort_GL = False
                                        break
                                else:
                                    m5th_scrol.insert(tk.END,'Force Buy(Mrg)... new_order Failed!!! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                    cnf.loop_AppMrgShTr = cnf.loopMrgGL + 1
                                    break
# !!!!!!!!!!!!!!!!!!!!!! BUY LIMIT with STOP LOSS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                        if cnf.isLMT_GL:
                            #db.get_open_orders_MRG_ShTr(cursor)
                            btype, pname, sorder, buyorder, sgotqty, sellprice, needcost, fprice, sverified, sloss, incomeV,incomeP, profit, CURR_LIMITS, sdtSec, isBub = BUY(cnf.orders_infoMrgShTr,bprice)  # -14-
# ---------------------- Check created sell order (there is in table) or not
                            if not buyorder:  # if is not order sell yet
                                new_order = newOrderM(pair_name_=pname, got_qty_=sgotqty, CURR_LIMITS_=CURR_LIMITS,need_cost_=needcost, side_='BUY', type_='LIMIT', mode='short')
                                db.store_buy_order_MRG_ShTr(cursor, conn, new_order['orderId'], sorder, sgotqty)
                                if 'orderId' in new_order and cnf.shortSQLiteGlbBuy: # check if Create order and Write to data base
                                    new_orderSL = new_order['orderId'] #orderID
                                    m5th_scrol.insert(tk.END, 'Buy(Mrg)... CREATE Order; ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                    dtSB = int(time.time())
                                else:
                                    m5th_scrol.insert(tk.END, 'Buy(Mrg)... Create and write FALSE! cnf.longSQLiteGlbBuy = ' + str(cnf.shortSQLiteGlbBuy) +'; ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                    msg.showinfo("mrgTradeShTr", 'Buy(Mrg)... Some problem when creating a new order!')
                            else:
                                new_orderSL = buyorder
                                m5th_scrol.insert(tk.END, 'Buy(Mrg)... CREATED Order Repeated! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                dtSB = int(time.time())
                            print('Buy(Mrg)... Short Trend -isBuing- sorder: ' + str(sorder) + '; buyorder: ' + str(buyorder)+ '; new_orderSL: ' + str(new_orderSL))
                            if new_orderSL:
                                isForce = 1
                                while order_statusB:
                                    blprice = round(float(cnf.bot.tickerPrice(symbol=cnf.symbolPairGL)['price']), 2)
                                    m4th_scrol.delete(0.1, tk.END)
                                    btype, pname, sorder, buyorder, sgotqty, sellprice, needcost, fprice, sverified, sloss, incomeV,incomeP, profit, CURR_LIMITS, sdtSec, isBub = BUY(cnf.orders_infoMrgShTr,blprice)  # -14-
                                    buystatus, time_passedS, time_passedM, iprice = OrderInfo(pname,new_orderSL,dtSB)
                                    if buystatus == 'FILLED':
                                        db.update_buy_order_MRG_ShTr(cursor, conn, sorder, blprice, incomeV, isForce)
                                        if cnf.shortSQLiteGlb:
                                            m5th_scrol.insert(tk.END, 'Buy(Mrg)... COMPLETE ' + str(dt.now().strftime('%H:%M:%S'))+ '\n' + 'Income($)-> ' + str(incomeV) + '; ' + '; Time passed min. -> ' + str(time_passedM) + '\n\n')
                                        else:
                                            msg.showinfo("mrgTradeShTr",'Buy... Some problem when write to DB!')
                                        cnf.loop_AppMrgShTr += 1
                                        cnf.AppMrg_freezShort_GL = False
                                        isBuing = False  # exit from isBuing
                                        break
                                    if buystatus == 'NEW':
                                        m4th_scrol.insert(tk.END,'Buy(Mrg)... Short Trend; Profit/StopLoss -> ' + str(profit) + '/' + str(sloss) + '\n' + 'Current rate -> ' + str(blprice) + '\n' + 'Sold -> ' + str(sellprice) +
                                                          '\n' + 'Aim price -> ' + str(needcost) + '\n' + 'Force sell -> ' + str(fprice) + '\n' + 'Income(%) -> ' + str(incomeP) + ' %\n'+ str(cnf.BUYshrt_LIFE_TIME_MIN)+' min. limit; ..... time passed min. ' + str(time_passedM) + '\n')

                                        if time_passedM > cnf.BUYshrt_LIFE_TIME_MIN and isBub and buystatus != 'PARTIALLY_FILLED':
                                            m4th_scrol.insert(tk.END, 'Time passed ->  ' + str(time_passedM) + ' min. Exit Order: ' + str(new_orderSL) + '\n')
                                            cancel = cnf.client.cancel_margin_order(symbol=pname, orderId=new_orderSL)
                                            if 'orderId' in cancel:
                                                m5th_scrol.insert(tk.END, 'Buy... Order Cancel SUCCESSFULLY! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                                new_order = newOrderM(pair_name_=pname, got_qty_=sgotqty,CURR_LIMITS_=CURR_LIMITS,need_cost_=0, side_='BUY', type_='MARKET', mode='short')
                                                new_orderSL = new_order['orderId']
                                                if new_orderSL:
                                                    m5th_scrol.insert(tk.END,'BuyBub... CREATE Market Order. ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                                else:
                                                    m5th_scrol.insert(tk.END,'BuyBub... -LIMIT- new_order Failed!!! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                                    msg.showinfo("mrgTradeShTr",'BuyBub... Some problem when creating a new order!')
                                            else:
                                                m4th_scrol.insert(tk.END, 'Buy(Mrg)... MACD -LIMIT- Order Cancel FAILD!!! ' + str(dt.fromtimestamp(int(time.time()))) + '\n')
                                                msg.showinfo("mrgTradeShTr",'BuyBub... Some problem when cancel order!')
                                    if buystatus == 'PARTIALLY_FILLED':
                                        m4th_scrol.insert(tk.END, 'Buy(Mrg)... ShortTrend -LIMIT- Status is ->  ' + str(buystatus) + '; Current rate -> ' + str(blprice)+ '\n')
                                    if buystatus == 'CANCELED':
                                        m5th_scrol.insert(tk.END,'CANCELED!!! new_orderId:  ' + str(new_orderSL)  + '; dt -> ' + str(dt.fromtimestamp(int(time.time()))) + '\n\n') # Buy(Mrg)... CREATED Order Repeated!!!!!!!!!!!!!!!!!???????????????? buy market
                                        cnf.AppMrg_freezShort_GL = False
                                        isBuing = False  # exit from isBuing
# ------    ----------------------- BUY LIMIT when STOP LOSS ----------------------
                                    if fprice < blprice and sloss > 0 and buystatus != 'PARTIALLY_FILLED':
                                        print("Force  Buy(Mrg)... ShortTrend -LIMIT- fprice {sl} - curate {cr}".format(sl=fprice, cr=blprice))
                                        mcancel = cnf.client.cancel_margin_order(symbol=pname, orderId=new_orderSL)
                                        time.sleep(2)
                                        if 'orderId' in mcancel:
                                            m5th_scrol.insert(tk.END, 'Force Buy... Order Cancel SUCCESSFULLY! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                            new_orderF = newOrderM(pair_name_=pname, got_qty_=sgotqty,CURR_LIMITS_=CURR_LIMITS, need_cost_=0,side_='BUY', type_='MARKET',mode='short')  # force sell
                                            #time.sleep(2)
                                            #db.update_buy_lmt_MRG(cursor, conn, sorder, new_orderF['orderId'])  # UPDATE order_Id(Force buy) same record in store_buy_order_MRG ????
                                            isForce = 0
                                            new_orderSL= new_orderF['orderId']
                                            if new_orderSL:
                                                m5th_scrol.insert(tk.END, 'Force Buy... CREATE Market Order. ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                            else:
                                                m5th_scrol.insert(tk.END,'Force Buy(Mrg)... -LIMIT- new_order Failed!!! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                                msg.showinfo("mrgTradeShTr",'Force Buy(Mrg)... Some problem when creating a new order!')
                                        else:
                                            m5th_scrol.insert(tk.END,'Force Buy... -LIMIT- Order Cancel FAILD!!! ' + str(dt.fromtimestamp(int(time.time()))) + '\n\n')
                                            msg.showinfo("mrgTradeShTr",'Force Buy... Some problem when cancel order!')
                                    time.sleep(6)  # 6sec
                            else:
                                m5th_scrol.insert(tk.END, 'Buy(Mrg)... -LIMIT- new_order Failed!!! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                # cnf.loop_AppMrgShTr = cnf.loopMrgGL + 1
                                # break

                        if not isBuing: break  # Exit from loop isBuing
                    else:
                        print('ERROR Buy... Short Trend - Sell do not accept (not verified) !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ')
                    thread = threading.Thread(target=run_progressbar(pb00_, delay_))
                    thread.start()
# !!!!!!!!!!!!! SELL SELL SELL !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            else:
                while isSelling and cnf.AppMrg_freezShort_GL:
                    # Получаем свечи и берем цены закрытия, high, low
                    klines = cnf.bot.klines(symbol=cnf.symbolPairGL,interval=cnf.KlineMrgGL,limit=cnf.KLINES_LIMITS)
                    klinesMinusLast = klines[:len(klines) - int(cnf.USE_OPEN_CANDLES)]
                    opens = [float(x[1]) for x in klinesMinusLast]
                    closes = [float(x[4]) for x in klinesMinusLast]
                    price = round(float(cnf.bot.tickerPrice(symbol=cnf.symbolPairGL)['price']), 2)
                    isUp, isBigUp, isDn, isBigDn = ta.ShortTrend(closes[-int(cnf.fastMoveCount):],opens[-int(cnf.fastMoveCount):])

                    if not cnf.isWork_or_Mrg_ShTr:
                        m1th_scrol.delete(0.1, tk.END)
                        m1th_scrol.insert(tk.END, '# Working Margin use ShortTrend! (mrgTradeMACD) #' + '\n' + '      (When selling in progress it freez!) ' + '\n\n')
                        m1th_scrol.insert(tk.END, 'KLINES_LIMITS(period)-> ' + str(cnf.KLINES_LIMITS) + '\n' + 'TIMEFRAME(in minutes)-> ' + str(cnf.KlineMrgGL) + '\n')
                        m1th_scrol.insert(tk.END, 'Sell  LIFE_TIME_MIN-> ' + str(cnf.SELLshrt_LIFE_TIME_MIN) + '\n' + 'Buy LIFE_TIME_MIN-> ' + str(cnf.BUYshrt_LIFE_TIME_MIN) + '\n')
                        m1th_scrol.insert(tk.END, '------------------------------------------------\n\n'+ str(dt.fromtimestamp(int(time.time()))) + '\n')
                        m1th_scrol.insert(tk.END, 'Is Market/Limit? -> ' + str(cnf.isMRKT_GL) + '/' + str(cnf.isLMT_GL) + '\n' + 'Is 3 candles Grow/Down?    -> ' + str(isUp) + '/' + str(isDn)+ '\n')
                        m1th_scrol.insert(tk.END, 'Is last candle Grow/Down? -> ' + str(isBigUp) + '/' + str(isBigDn) + '\nRate             -> ' + str(price) + '\n------------------------------------------------\n')
                    pname, amount, spendsumMRG, profit, stoploss, CURR_LIMITS, sdt = SELL(price)  # -8-
# !!!!!!!!!!!!!!!!!!!!!! SELL MARKET if fast Grow last candel !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    if (isUp or isBigUp) and cnf.isMRKT_GL:  # if SHORT TREND or STARTED from HSTREmulate and Market
                        print('Sell(Mrg)... ShortTrend -MARKET-  if isUp {iu} isBigUp {ibu} isMRKT_GL  {m}'.format(iu=isUp, ibu=isBigUp,m=cnf.isMRKT_GL))
                        new_order = newOrderM(pair_name_=pname, got_qty_=amount, CURR_LIMITS_=CURR_LIMITS, need_cost_=0,side_='SELL', type_='MARKET', mode='short')
                        db.add_new_order_SELL_MRG_ShTr(cursor, conn, pname, new_order['orderId'], amount, price, spendsumMRG, profit, stoploss, 'market')  # -10-
                        if 'orderId' in new_order:
                            m5th_scrol.insert(tk.END, 'Sell(Mrg)... CREATE ShortTrend -MARKET- Pair-> ' + str(pname) + '\n' + 'Price-> ' + str(price) + '; Amount: ' + str(amount) + '; ' + str(dt.fromtimestamp(int(time.time()))) + '\n')
                            order_status, time_passedS, time_passedM, iprice = OrderInfo(pname, new_order['orderId'],sdt)
                            if order_status == 'FILLED':
                                db.update_sell_MRG_ShTr(cursor, conn, new_order['orderId'], price)
                                m5th_scrol.insert(tk.END, '............ COMPLETE! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                isSelling = False
                                break  # terminate loop -isSelling-
                            else:
                                m5th_scrol.insert(tk.END, 'Create Sell Order do not FILLED!  '+ str(dt.now().strftime('%H:%M:%S')) + '\n')
                                isSelling = False
                                break  # terminate loop -isSelling-
                        else:
                            m5th_scrol.insert(tk.END,'orderId is not in new_order!!! ' + str(dt.now().strftime('%H:%M:%S')) + '\n\n')
                            isSelling = False
                            break  # terminate loop -isSelling-

# !!!!!!!!!!!!!!!!!!!!!! SELL LIMIT with TIMER if fast Grow last candel !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    if ((isUp or isBigUp) and cnf.isLMT_GL) or (sell_order and cnf.isLMT_GL):  # if Short trend or started from HSTREmulate and Limit
                        #need_priceLMT = round(price + cnf.nLMTautoUpMrg_GL, 2)  # 5$ buy low on base crypto ????????? we need correcting sellLMT
                        if cnf.nLMT_GL_CheckB == 0:
                            need_priceLMT = round(price - cnf.nLMT_MrgGL, 2)
                        else:
                            need_priceLMT = round(price + cnf.nLMTautoUpMrg_GL, 2)
                        print('mrgTradeShTr()... cnf.nLMT_GL_CheckB: ' + str(cnf.nLMT_GL_CheckB) + '; cnf.nLMT_auto: ' + str(cnf.nLMTautoUpMrg_GL) + '; cnf.nLMT_MrgGL: ' + str(cnf.nLMT_MrgGL))
                        if not sell_order:  # create first buy order
                            print('Sell(Mrg)...ShortTrend -LIMIT- Price-> ' + str(price) + '; need_priceLMT: ' + str(need_priceLMT)+ '; cnf.nLMTautoUpMrg_GL: ' + str(cnf.nLMTautoUpMrg_GL))
                            #pname, amount, spendsumMRG, profit, stoploss, CURR_LIMITS, sdt = SELL(price)  # -8-
                            new_order = newOrderM(pair_name_=pname, got_qty_=amount, CURR_LIMITS_=CURR_LIMITS, need_cost_=need_priceLMT, side_='SELL', type_='LIMIT', mode='short')
                            db.add_new_order_SELL_MRG_ShTr(cursor, conn, pname, new_order['orderId'], amount, need_priceLMT, spendsumMRG, profit, stoploss,'limit') # -10-
                            if 'orderId' in new_order and cnf.shortSQLiteGlb: # check if Create order and Write to data base
                                new_orderId = new_order['orderId']
                                m5th_scrol.insert(tk.END, 'Sell(Mrg)... CREATED! ShortTrend LIMIT; ' + str(pname) + '\nPrice-> ' + str(price) + '; Amount: ' + str(amount) + '; ' + str(dt.fromtimestamp(int(time.time()))) +
                                                  '; cnf.bigUpPercent: ' + str(cnf.bigUpPercent)+ '; cnf.nLMTautoUpMrg_GL: ' + str(cnf.nLMTautoUpMrg_GL)+'\n')
                                dtSB = int(time.time())
                            else:
                                m5th_scrol.insert(tk.END, 'Sell(Mrg)... CREATED and write FALSE! ' + str(dt.now().strftime('%H:%M:%S')) + '\n\n')
                                cnf.AppMrg_freezShort_GL = False  # Exit from function
                                isSelling = False
                                break
                        else:
                            new_orderId = sell_order[0]
                            m5th_scrol.insert(tk.END, 'Sell(Mrg)... CREATE ShortTrend -LIMIT- Repeated! ' + str(dt.now().strftime('%H:%M:%S')) + '\nNeed Price-> ' + str(need_priceLMT) + '\n')
                            #m5th_scrol.insert(tk.END, 'Sell(Mrg)... test sell_order: ' + str(type(sell_order)) + str(sell_order[0]) + '\n')
                            dtSB = int(time.time())
                        if new_orderId:
                            while order_statusS:
                                slprice = round(float(cnf.bot.tickerPrice(symbol=cnf.symbolPairGL)['price']), 2)
                                m4th_scrol.delete(0.1, tk.END)
                                order_status, time_passedS, time_passedM, iprice = OrderInfo(pname, new_orderId, dtSB)
                                if order_status == 'FILLED':
                                    db.update_sell_MRG_ShTr(cursor, conn, new_orderId, need_priceLMT)
                                    m5th_scrol.insert(tk.END, '............ COMPLETE! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                    isSelling = False
                                    break
                                if order_status == 'NEW':
                                    m4th_scrol.insert(tk.END,'Sell(Mrg)...ShortTrend -LIMIT- Status NEW \nCurrent rate-> ' + str(slprice) + '\nAim         -> ' + str(need_priceLMT) + '\n..... time passed min. ' + str(time_passedM) + '\n')
                                    print('Sell(Mrg)...ShortTrend -LIMIT- Current rate-> ' + str(slprice) + '; Aim-> ' + str(need_priceLMT) + '\n..... time passed min. ' + str(time_passedM) + '\n')
                                    if time_passedM > cnf.SELLshrt_LIFE_TIME_MIN and order_status != 'PARTIALLY_FILLED':
                                        cancel = cnf.client.cancel_margin_order(symbol=pname, orderId=new_orderId)
                                        db.update_sell_Cancel_MRG_ShTr(cursor, conn, new_orderId)
                                        # Если удалось отменить ордер, скидываем информацию в БД
                                        if ('orderId' in cancel) and cnf.shortSQLiteGlb:
                                            print("Sell(Mrg)... ShortTrend -LIMIT- Ордер {order} был успешно отменен".format(order=new_orderId))
                                            m5th_scrol.insert(tk.END,'Sell(Mrg)...  Order Cancel SUCCESSFULLY! ' + str(dt.now().strftime('%H:%M:%S')) + '\n\n')
                                            cnf.AppMrg_freezShort_GL = False # Exit from function
                                            isSelling = False
                                            break
                                        else:
                                            m5th_scrol.insert(tk.END,'Sell(Mrg)... -LIMIT- Cancel order Failed!!!!!!!!!! order: ' + str(cancel))
                                            print('Sell(Mrg)... -LIMIT- Cancel order Failed!!!!!!!!!! order: ' + str(cancel))
                                            msg.showinfo("mrgTradeShTr",'Sell(Mrg).... MACD Failed Cancel order or Write DB!')
                                            isSelling = False
                                            break
                                    #m4th_scrol.insert(tk.END, 'Sell(Mrg)...ShortTrend Status is ->  ' + str(order_status) + '; dt -> ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                if order_status == 'PARTIALLY_FILLED':
                                    print("Sell(Mrg)... ShortTrend -LIMIT- Ордер {order} частично исполнен, ждем завершения".format(order=new_orderId))
                                    m4th_scrol.insert(tk.END, 'Sell(Mrg)... ShortTrend PARTIALLY_FILLED ' + '\n' + '..... time passed min. ' + str(time_passedM) + '; dt -> ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                if order_status == 'CANCELED':
                                    db.update_sell_Cancel_MRG_ShTr(cursor, conn,new_orderId)
                                    m4th_scrol.insert(tk.END, 'Sell(Mrg)... ShortTrend -LIMIT- Status is -> CANCELED! ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                                    cnf.AppMrg_freezShort_GL = False  # Exit from function
                                    isSelling = False
                                    break
                                #m4th_scrol.insert(tk.END, 'Sell(Mrg)... ShortTrend -LIMIT- Status is ->  ' + str(order_status) + '; time passed -> ' + str(time_passedM) +str(' min.\n'))
                                time.sleep(6)  # 6 sec
                        else:
                            m5th_scrol.insert(tk.END, 'orderId is not in new_orderL!!!  ' + str(dt.now().strftime('%H:%M:%S')) + '\n')
                            isSelling = False
                            break  # terminate loop -isSelling-
                    if not isSelling: break  # Exit from loop isSelling

                    thread = threading.Thread(target=run_progressbar(pb00_, cnf.chVarDelay_GL))
                    thread.start()
            if cnf.loop_AppMrgShTr >= cnf.loopMrgGL:
                m4th_scrol.insert(tk.END, 'mrgTradeShTr TERMINATE! Loop = ' + str(cnf.loop_AppMrgShTr) + '; ' + str(dt.now().strftime('%H:%M:%S'))+ '\n')
                cnf.AppMrg_freezShort_GL = False
        except Exception as e:
            print("ERROR mrgTradeShTr().... from WHILE cnf.loop_AppMrgShTr {}".format(e))
            time.sleep(10)
            continue
    m4th_scrol.insert(tk.END, 'mrgTradeShTr TERMINATE - End Function! loop_AppMrgShTr = ' + str(cnf.loop_AppMrgShTr) + '; ' + str(dt.now().strftime('%H:%M:%S'))+ '\n')
    cursor.close()
def SELL(price):
    if cnf.pairsGL:
        for pair_name, pair_obj in cnf.pairsGL.items():
            # Получаем лимиты пары с биржи
            for elem in limits['symbols']:
                if elem['symbol'] == pair_name:
                    CURR_LIMITS = elem
                    break
            else:
                raise Exception("SELL()...Не удалось найти настройки выбранной пары " + pair_name)
            #price = round(float(cnf.bot.tickerPrice(symbol=pair_name)['price']),2)
            # Рассчитываем кол-во, которое можно купить на заданную сумму, и приводим его к кратному значению
            my_amount = adjust_to_step(float(pair_obj['spend_sum_mrg']), CURR_LIMITS['filters'][2]['stepSize'])
            if my_amount < float(CURR_LIMITS['filters'][2]['stepSize']) or my_amount < float(CURR_LIMITS['filters'][2]['minQty']):
                print("SELL()...Покупка невозможна, выход. Увеличьте размер ставки!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                continue
            # Итоговый размер лота
            trade_am = price * my_amount

            # Если итоговый размер лота меньше минимального разрешенного, то ругаемся и не создаем ордер
            if trade_am < float(CURR_LIMITS['filters'][3]['minNotional']):
                raise Exception("SELL()... Увеличьте сумму торгов!!!!!!!!!!!!!!!!")

            return pair_name, my_amount, pair_obj['spend_sum_mrg'], pair_obj['profit_markupMrg'], pair_obj['stop_lossMrg'], CURR_LIMITS, int(time.time())

    else:
        print("Error from SELL()... init varibale (press button Init)!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

def BUY(orders_info,price):
    isBub = False
    try:
       for order, value in orders_info.items():
           # смотрим, какие ограничения есть для создания ордера на покупку
           for elem in limits['symbols']:
               if elem['symbol'] == value['order_pair']:
                   CURR_LIMITS = elem
                   break
           else:
               raise Exception("Не удалось найти настройки выбранной пары " + orders_info[order]['order_pair'])

           if value['panic_fee'] > 0:
               fbuy_price = round(value['sell_price'] * (100 + value['panic_fee']) / 100,2)
           else:
               fbuy_price = 0
           sell_dt = dt.strptime(value['sell_finished'],'%Y-%m-%d %H:%M:%S')#/1000)
           sell_dtINT = int(sell_dt.strftime("%Y%m%d%H%M%S"))
           #time_passedSec = int(time.time()) - sell_dtINT

           profit_markup = cnf.pairsGL[value['order_pair']]['profit_markup']
           got_qty = adjust_to_step(value['sell_amount'], CURR_LIMITS['filters'][2]['stepSize'])
           #price = float(cnf.bot.tickerPrice(symbol=value['order_pair'])['price'])
           need_cost = round((got_qty * value['sell_price'] * (1 - profit_markup / 100 - 0.0015)) / got_qty,2) # commission with BNB
           incomeV = round((got_qty * value['sell_price']) * (1 - 0.00075) - (got_qty * price) * (1 - 0.00075),4)  # commission 0.075% sequnces not in percent
           incomeP = round((value['sell_price']/price - 1) * 100, 2) # in percent

           #Calculate breakeven
           bub = value['sell_price'] * (1 - 0.0015)
           #print("BUY()... BUB IS ------------> {}".format(bub))
           if price < bub:
               isBub = True
           sellDate = dt.strptime(value['sell_finished'],'%Y-%m-%d %H:%M:%S')  # преобразует строку в datetime; timestamp() - возвращает время в секундах с начала эпохи.
           sellDateSec = sellDate.timestamp()

           return value['order_type'],value['order_pair'], order, value['buy_order_id'], got_qty, value['sell_price'], need_cost, fbuy_price, value['sell_verified'], value['panic_fee'], incomeV, incomeP,profit_markup, CURR_LIMITS,sellDateSec,isBub

    except Exception as e:
        print("Error from BUY()... in AppMargin {}".format(e))

def OrderInfo(name,ordID,dti):
    order_status, time_passedSec, time_passedMin,price = 0,0,0,0
    try:
        #st = cnf.client.get_server_time()
        #stint = int(cnf.client.get_server_time()) / 1000
        #https://github.com/binance-exchange/binance-official-api-docs/blob/master/margin-api.md#query-margin-accounts-order-user_data     Get /sapi/v1/margin/order Response
        stock_order_data = cnf.client.get_margin_order(symbol=name, orderId=ordID) # , recvWindow=10000)
        print('OrderInfo()... Stock_order_data-> ' + str(stock_order_data))
        order_status = str(stock_order_data['status'])
        price = round(float(stock_order_data['price']),2)
        if order_status in cnf.ORDER_STATUS:
            print('OrderInfo()... order_status ', order_status)
        else:
            order_status = 'do not exist'
        # print('OrderInfo()... Server time fromtimestamp-> ' + str(dt.fromtimestamp(stint)))
        # print('OrderInfo()... Order time fromtimestamp-> ' + str(dt.fromtimestamp(round(stock_order_data['time']/1000))))
        # print('OrderInfo()... Local time fromtimestamp-> ' + str(dt.fromtimestamp(int(time.time()))))
        time_passedSec = int(time.time()) - dti
        time_passedMin = round(time_passedSec / 60, 2)
        #curr_rate = round(float(cnf.bot.tickerPrice(symbol=name)['price']),2)
    except Exception as e:
        print("Error Error Error from OrderInfo()- {}".format(e))
    return order_status, time_passedSec, time_passedMin,price

def StaticSession(m1th_scrol):
    m1th_scrol.delete(0.1, tk.END)
    m1th_scrol.insert(tk.END, 'LONG Statistics for session:\n')
    m1th_scrol.insert(tk.END, 'Profit trades Count/Profit-> ' + str(cnf.appProfit_GL[0])+'/'+str(round(cnf.appProfit_GL[1],2)) + '\n')
    m1th_scrol.insert(tk.END, 'Loss trades   Count/Profit-> ' + str(cnf.appProfit_GL[2])+'/'+str(round(cnf.appProfit_GL[3],2)) + '\n\n')
    m1th_scrol.insert(tk.END, 'MARGIN Statistics for session:\n')
    m1th_scrol.insert(tk.END, 'Profit trades Count/Profit-> ' + str(cnf.appMrgProfit_GL[0])+'/'+str(round(cnf.appMrgProfit_GL[1],2)) + '\n')
    m1th_scrol.insert(tk.END, 'Loss trades   Count/Profit-> ' + str(cnf.appMrgProfit_GL[2])+'/'+str(round(cnf.appMrgProfit_GL[3],2)) + '\n\n')
