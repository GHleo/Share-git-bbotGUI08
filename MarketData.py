#Class for get and init market Data

import threading
import AppEmulate
import AppWork
import AppEmMargin
import AppMargin
import configGlb as cnf
import ta
from datetime import datetime as dt

# ===================================================================
class MarketData:

    def __init__(self):  # Initializer method!
        self.curr_rate = round(float(cnf.bot.tickerPrice(symbol='BTCUSDT')['price']), 2)
        self.klines24h = cnf.client.get_klines(symbol=cnf.symbolPairGL, interval='6h', limit=4)
        self.klines4h = cnf.client.get_klines(symbol=cnf.symbolPairGL, interval='1h', limit=4)
        self.closes24h = [float(x[4]) for x in self.klines24h]
        self.volume24 = [float(x[5]) for x in self.klines24h]
        self.volumeQ24 = [float(x[7]) for x in self.klines24h]
        self.closes4h = [float(x[4]) for x in self.klines4h]
        self.volume4 = [float(x[5]) for x in self.klines4h]


        klines = cnf.client.get_klines(symbol=cnf.symbolPairGL, interval=cnf.KlineGL, limit=cnf.KLINES_LIMITS)
        klinesMinusLast = klines[:len(klines) - int(cnf.USE_OPEN_CANDLES)]
        closes = [float(x[4]) for x in klinesMinusLast]
        opens = [float(x[1]) for x in klinesMinusLast]
        high = [float(x[2]) for x in klinesMinusLast]
        low = [float(x[3]) for x in klinesMinusLast]
        closes_time = [float(x[6]) for x in klinesMinusLast]
        dt_ = [dt.fromtimestamp(round(x / 1000)) for x in closes_time]
        dt_HM = [dt.strftime(x,'%H:%M') for x in dt_]

    def printTest(self):
        #self.klines24h = cnf.client.get_klines(symbol=cnf.symbolPairGL, interval='6h', limit=4)
        mtmPrd24, mtmPrd4 = self.MTM() #return 24h, 12h, 6h
        print('printTest()... \nmtmPrd24: ' + str(mtmPrd24) + '\nmtmPrd4: ' + str(mtmPrd24))
        print('printTest()... \ncurrent rate: ' + str(self.curr_rate))
    # Momentum for periods 24 and 4 hours
    def MTM(self):
        try:
            Cl_first24, Cl_half24, Cl_last24 = self.closes24h[0], self.closes24h[1],self.closes24h[-1]
            Cl_first4, Cl_half4, Cl_last4 = self.closes4h[0], self.closes4h[1], self.closes4h[-1]

            mtmPrd24 = [0, 0, 0]
            mtmPrd24[0] = round((Cl_last24 - Cl_first24) / Cl_last24 * 100, 2), round(Cl_last24 - Cl_first24, 2) #mtm for 24 hours
            mtmPrd24[1] = round((Cl_last24 - Cl_half24) / Cl_last24 * 100, 2), round(Cl_last24 - Cl_half24, 2) #mtm for 12 hours
            mtmPrd24[2] = round((Cl_last24 - self.closes24h[-2]) / Cl_last24 * 100, 2), round(Cl_last24 -self.closes24h[-2], 2) #mtm for last 6 hours

            mtmPrd4 = [0, 0, 0]
            mtmPrd4[0] = round((Cl_last4 - Cl_first4) / Cl_last4 * 100, 2), round(Cl_last4 - Cl_first4, 2)#mtm for 4 hours
            mtmPrd4[1] = round((Cl_last4 - Cl_half4) / Cl_last4 * 100, 2), round(Cl_last4 - Cl_half4, 2)#mtm for 2 hours
            mtmPrd4[2] = round((Cl_last4 - self.closes4h[-2]) / Cl_last4 * 100, 2), round(Cl_last4 - self.closes4h[-2], 2) #mtm for last 1 hour

            print('self.closes24h: ' + str(self.closes24h) + '\nself.closes4h: ' + str(self.closes4h))
            print('Cl_first4: ' + str(Cl_first4) + '\nCl_half4: ' + str(Cl_half4) + '\nCl_last4: ' + str(Cl_last4))

            return mtmPrd24, mtmPrd4
        except Exception as e:
            print('Exception from MarketData.MTM ', e)