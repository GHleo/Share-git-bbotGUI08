import time
from datetime import datetime
#from trades import BaseTrade
import configGlb as cnf
import keys
from binance.client import Client

# Ф-ция, которая приводит любое число к числу, кратному шагу, указанному биржей
# Если передать параметр increase=True то округление произойдет к следующему шагу
def adjust_to_step(value, step, increase=False):
   return ((int(value * 100000000) - int(value * 100000000) % int(
        float(step) * 100000000)) / 100000000)+(float(step) if increase else 0)


# синхронизирует локальное время и время биржи
def sync_time(bot, log, pause, limits):
    while True:
        try:
            # Получаем ограничения торгов по всем парам с биржи
            local_time = int(time.time())
            server_time = int(limits['serverTime']) // 1000

            # Бесконечный цикл программы
            shift_seconds = server_time - local_time

            if local_time + shift_seconds != server_time:
                bot.set_shift_seconds(shift_seconds)

                log.debug("""
                    Текущее время: {local_time_d} {local_time_u}
                    Время сервера: {server_time_d} {server_time_u}
                    Разница: {diff:0.8f} {warn}
                    Бот будет работать, как будто сейчас: {fake_time_d} {fake_time_u}
                """.format(
                    local_time_d=datetime.fromtimestamp(local_time), local_time_u=local_time,
                    server_time_d=datetime.fromtimestamp(server_time), server_time_u=server_time,
                    diff=abs(local_time - server_time),
                    warn="ТЕКУЩЕЕ ВРЕМЯ ВЫШЕ" if local_time > server_time else '',
                    fake_time_d=datetime.fromtimestamp(local_time + shift_seconds), fake_time_u=local_time + shift_seconds
                ))

        except:
            log.exception('sync_time error')

        if pause:
            time.sleep(10000)
        else:
            break

def calc_buy_avg_rate(order_trades):
    bought = 0
    spent = 0
    fee = 0
    avg_rate = 0
    for trade in order_trades:
        bought += trade.trade_amount
        spent += trade.trade_amount * trade.trade_rate
        fee += trade.trade_fee
        # print('!!!! From calc_buy_avg_rate: ' + str(trade))
        # log.debug(
        #     'По ордеру была сделка {id} на покупку {am:0.8f} по курсу {r:0.8f}, комиссия {fee:0.8f} {f_a}'.format(
        #         id=trade.trade_id,
        #         am=trade.trade_amount,
        #         r=trade.trade_rate,
        #         fee=trade.trade_fee,
        #         f_a=trade.fee_type
        #     ))
    try:
        avg_rate = spent / bought
    except ZeroDivisionError:
        print('Не удалось посчитать средневзвешенную цену, деление на 0')
        avg_rate = 0
    print('!!!! From calc_buy_avg_rate Средневзвешенная цена: ' + str(avg_rate))

    return avg_rate

def calc_sell_avg_rate(order_trades):
    sold = 0
    got = 0
    fee = 0

    for trade in order_trades:

        sold += trade.trade_amount
        got += trade.trade_amount * trade.trade_rate
        fee += trade.trade_fee

        # log.debug(
        #     'По ордеру была сделка {id} на продажу {am:0.8f} по курсу {r:0.8f}, комиссия {fee:0.8f} {f_a}'.format(
        #         id=trade.trade_id,
        #         am=trade.trade_amount,
        #         r=trade.trade_rate,
        #         fee=trade.trade_fee,
        #         f_a=trade.fee_type
        #     ))

    try:
        avg_rate = got / sold
    except ZeroDivisionError:
        #log.debug('Не удалось посчитать средневзвешенную цену, деление на 0')
        avg_rate = 0

    #log.debug('Средневзвешенная цена {ar:0.8f}'.format(ar=avg_rate))

    return avg_rate

# def get_order_trades(order_id, pair, bot, mode):  SEE in bbotGUI07 trades.py
#
#     if mode == 'standart': trades = bot.myTrades(symbol=pair)
#     if mode == 'short': trades = bot.marginMyTrades(symbol=pair)
#     trades.reverse()
#
#     ret_trades = []
#     for trade in trades:
#         if str(trade['orderId']) == str(order_id):
#             ret_trades.append(
#                 BaseTrade(
#                     trade_id=trade['id'],
#                     trade_rate=float(trade['price']),
#                     trade_amount=float(trade['qty']),
#                     trade_type='buy' if trade['isBuyer'] else 'sell',
#                     trade_fee=float(trade['commission']),
#                     fee_type=trade['commissionAsset']
#                 )
#             )
#     return ret_trades

def MA_Cross(maFast,maSlow):
    fastHigh = False
    fastUnder = False
    cross = False
    if (maFast[-2] > maSlow[-2]) and (maFast[-1] > maSlow[-1]):
        fastHigh = True
    if (maFast[-2] < maSlow[-2]) and (maFast[-1] < maSlow[-1]):
        fastUnder = True
    if not fastHigh  and not fastUnder:
        cross = True
    return cross

def MA_Cross_Modern(maFast,maSlow):
    crossUp = False
    crossDn = False
    if (cnf.maFast_prev < cnf.maSlow_prev) and (maFast[-1] > maSlow[-1]):
        crossUp  = True
    if (cnf.maFast_prev > cnf.maSlow_prev) and (maFast[-1] < maSlow[-1]):
        crossDn  = True

    cnf.maFast_prev = maFast[-1]
    cnf.maSlow_prev = maSlow[-1]
    return  crossUp, crossDn
# MACD cross Zero line
def macdCross(macd):
    crossUp = False
    crossDn = False

    if (cnf.macd_prev < 0) and (macd[-1] >= 0):
        crossUp = True
    if (cnf.macd_prev > 0) and (macd[-1] <= 0):
        crossDn = True

    cnf.macd_prev = macd[-1]

    return crossUp, crossDn

# MACD cross Signal line
def macdSignalCross(macd,macdSign):
    crossUp = False
    crossDn = False
    #print('macdSignalCross()... macd: ', macd)

    if (macd[-2] <= macdSign[-2]) and (macd[-1] >= macdSign[-1]) and (macd[-1] < 0):  #all(i < 0 for i in macd):
        crossUp = True
        #print('macdSignalCross()... crossUp! macd: ' + str(macd) + '; macdSign: '+ str(macdSign))
    if (macd[-2] >= macdSign[-2]) and (macd[-1] <= macdSign[-1]) and (macd[-1] > 0): #all(i > 0 for i in macd):
        crossDn = True
        #print('macdSignalCross()... crossDn! macd: ' + str(macd) + '; macdSign: '+ str(macdSign))

    return crossUp, crossDn

# MACD cross Signal line
def HSTRmacdSignalCross(macd,macdSign, cl, H, L):
    indexUp, indexDn = [], []
    i = 0
    # print('macd: ', macd)
    # print('macdSign: ' + str(macdSign) + '\n')
    for m, ms, cl, h, l in zip(macd, macdSign, cl, H, L):
        #if m is not None and ms is not None:
        if i < len(macd)-1:
            if macd[i-1] < macdSign[i] and macd[i] > macdSign[i+1]: #and (i != 0):
                #crossUp.append(macd[i])
                indexUp.append([i,cl])
                #print('UP i/close: ' + str(i)+'/'+ str(cl) + '\nmacd[i-1] ' + str(macd[i-1]) + ' <  macdSign[i] ' + str( macdSign[i]) + '\nmacd[i] ' + str(macd[i])+ ' > macdSign[i+1]: ' + str(macdSign[i+1]) + '\n')

            if (macd[i-1] > macdSign[i]) and (macd[i] < macdSign[i+1]): #and (i != 0):
                #crossDn.append(macd[i])
                indexDn.append([i,cl])
                #print('DN i/close: ' + str(i)+'/' + str(cl) + '\nmacd[i-1] ' + str(macd[i-1]) + ' >  macdSign[i] ' + str( macdSign[i]) + '\nmacd[i]: ' + str(macd[i])+ ' < macdSign[i+1]: ' + str(macdSign[i+1])+ '\n')

        i += 1
    #print('indexUp: ',indexUp)
    #print('indexDn: ',indexDn)
    #return crossUp, crossDn, indexUp, indexDn
    return indexUp, indexDn

def macdHCross(macdH):
    crossUp = False
    crossDn = False
    if (cnf.macdH_prev < 0) and (macdH[-1] >= 0):
        crossUp = True
    if (cnf.macdH_prev > 0) and (macdH[-1] <= 0):
        crossDn = True

    cnf.macdH_prev = macdH[-1]
    return crossUp, crossDn

def calcWR(wr,direction):
    if wr <= -80 and direction == 'long': return 0.1
    elif wr >= -20 and direction == 'short': return 0.1
    else:
        return 0


client = Client(keys.apikey, keys.apisecret)
def newOrderM(pair_name_, got_qty_, CURR_LIMITS_, need_cost_, side_, type_, mode):
    # Отправляем команду на создание ордера с рассчитанными параметрами
   # print('OOOO', pair_name_, got_qty_, CURR_LIMITS_, need_cost_, side_, type_, mode)
    #for Short trade
    if type_ == 'MARKET' and mode == 'short':
        #print('OOOO if type_ == MARKET and mode == short')
        new_order = cnf.client.create_margin_order(
        #new_order = cnf.bot.marginCreateOrder(
            symbol=pair_name_,
            side=side_, # SELL or BUY
            type=type_, # MARKET or LIMIT
            #timeInForce='GTC',
            quantity= "{quantity:0.{precision}f}".format(quantity=got_qty_, precision=CURR_LIMITS_['baseAssetPrecision'])
        )
    # for standart trade
    if type_ == 'MARKET' and mode == 'trade':
        new_order = cnf.bot.createOrder(
            symbol=pair_name_,
            recvWindow=5000,
            side=side_,
            type=type_,
            quantity="{quantity:0.{precision}f}".format(
                quantity=got_qty_, precision=CURR_LIMITS_['baseAssetPrecision']
            ),
            newOrderRespType='FULL'
        )
        # for Short trade
    if type_ == 'LIMIT' and mode == 'short':
        #new_order = cnf.bot.marginCreateOrder.create_margin_order(
        new_order=cnf.client.create_margin_order(
            symbol=pair_name_,
            side=side_,
            type=type_,
            timeInForce='GTC',
            quantity="{quantity:0.{precision}f}".format(quantity=got_qty_, precision=CURR_LIMITS_['baseAssetPrecision']
            ),
            price="{price:0.{precision}f}".format(price=need_cost_, precision=CURR_LIMITS_['baseAssetPrecision']
            ),
            newOrderRespType='FULL'
        )

    # for standart trade
    if type_ == 'LIMIT'and mode == 'trade':
        new_order = cnf.bot.createOrder(
            symbol=pair_name_,
            recvWindow=5000,
            side=side_,
            type=type_,
            timeInForce='GTC',
            quantity="{quantity:0.{precision}f}".format(quantity=got_qty_, precision=CURR_LIMITS_['baseAssetPrecision']
            ),
            price="{price:0.{precision}f}".format(price=need_cost_, precision=CURR_LIMITS_['baseAssetPrecision']
            ),
            newOrderRespType='FULL'
        )

    #time.sleep(2)#2 seconds
    #print('new_order: ', new_order)
    return new_order

def Portfolio():
    p=1

