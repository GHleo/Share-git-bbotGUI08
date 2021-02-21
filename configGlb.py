import keys
from binance_api import Binance
import logging
import os
from binance.client import Client

longSQLiteGlb, longSQLiteGlbSell, shortSQLiteGlb, shortSQLiteGlbBuy = False, False, False, False
bot = Binance(API_KEY=keys.apikey, API_SECRET=keys.apisecret)
client = Client(keys.apikey, keys.apisecret)
#AppWorkLMT.updatePortfolio()
#assetsArray = client.get_account()

pairs_ = ['BTC', 'ETH', 'BAT', 'BNB', 'NEO', 'ADA', 'TRX', 'BTT', 'LTC', 'MATIC','ALGO','IOTA','XEM']
pairs_2 = ['USDT', 'BTC', 'ETH', 'BAT', 'BNB', 'NEO', 'ADA', 'TRX', 'BTT', 'LTC', 'MATIC','ALGO']
mprofit = ['0.05', '0.1', '0.2', '0.3', '0.4', '0.5','0.6','0.7','0.8','0.9','1','1.2', '1.5','2', '3','6', '8']
moffers_amount = ['5', '10', '20', '50', '100', '500', '1000']
mstoploss = ['0','0.05','0.1','0.15','0.2','0.25','0.3','0.35','0.4','0.45','0.5','0.55', '0.6', '0.7','0.9', '1', '1.5', '2', '3', '4', '5']
mDelay = ['5','10','15','30','60']
mKline = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h','1d','3d', '1w', '1M'] #For combobox in oop.py
#mKlinePeriod = ['5min ago UTC','15min ago UTC',  '30min ago UTC', '1H ago UTC','2H ago UTC', '6H ago UTC', '12H ago UTC','24H ago UTC','48H ago UTC','1W ago UTC', '1M ago UTC','now UTC']
mKlineLimit = ['2','3','6','11','16', '21', '51', '86', '101', '200', '300', '400', '500']
cmdays = ['-1 days','-7 days','-14 days','-30 days','-60 days','-90 days','-180 days','-360 days']
pairs = [
            {
                'base': 'USDT',
                'quote': 'BTC',
                #'offers_amount': 5,  # Сколько предложений из стакана берем для расчета средней цены
                # Максимум 1000. Допускаются следующие значения:[5, 10, 20, 50, 100, 500, 1000]
                'spend_sum': 25,  # Сколько тратить base каждый раз при покупке quote
                'spend_sum_mrg':0, # Сколько тратить base каждый раз при покупке quote - Маржинальная торпговля
                'profit_markup': 0.005,  # Какой навар нужен с каждой сделки? (0.001 = 0.1%)
                'profit_markupMrg': 0.005,  # Какой навар нужен с каждой сделки? (0.001 = 0.1%)
                'use_stop_loss': True,  # Нужно ли продавать с убытком при падении цены
                'stop_loss': 2, # 2%  - На сколько должна упасть цена, что бы продавать с убытком
                'stop_lossMrg': 0
            }
            # {
            #     'base': 'USDT',
            #     'quote': 'ETH'
            # }
        ]
isWork_or_Mrg = True # if TRUE work - AppWork; if FALSE work AppMargin
isWork_or_Mrg_ShTr = False # if TRUE work - AppWork; if FALSE work AppMargin
chVarDelay_GL = 0

#WeightTrade = [0,0,0,0] #Calculate weight (CountNegTrade/CountTrade for period)
#********** AppWork
loopGL = 0 #Count for loop of AppWork and AppMargin
orders_infoMACD = {} # use in AppWork taTradeMACD()
orders_infoShTr = {} # use in AppWork taTradeShTrend()
loop_AppWrk = 0 #loop Flag for AppWork
loop_AppWrkShTr = 0 #loop Flag for AppWork
wdays = '' #get days from combo box for portfolio functions
App_freezLong_GL = False #Flag for freez algoritms ShortTrend or MACD Up _in AppWork
appProfit_GL = [0,0,0,0] # list for statistics of trade on session
KlineGL = '' #timeframe from ComboBox in AppWork and AppMargin


#********** AppMargin
is_mrgTrade = False
orders_infoMrgShTr = {}
orders_infoMrgMACD = {}
#loop_AppMrg = 0 #loop Flag for AppMargin
loop_AppMrgShTr = 0 #loop Flag for AppMargin
loop_AppMrgMACD = 0 #loop Flag for AppMargin
taTradeMRGBtn_GL = False # enable/disable button taTrade
taTradeMMRGBtn_GL = False # enable/disable button taTrade
AppMrg_freezShort_GL = False #Flag for freez algoritms ShortTrend or MACD Dn in AppmMargin
appMrgProfit_GL = [0,0,0,0] # list for statistics of trade on session
KlineMrgGL = '' #timeframe from ComboBox in AppWork and AppMargin

#********** AppEmulate
loopMrgGL = 0 #Count for loop of AppEmulate and AppEmMargin
is_taTrade = False #working or not _taTrade
loop_AppEmul = 0 #loop Flag for AppEmulate e_taTrade()
loop_AppEmulShTr = 0 #loop Flag for AppEmulate e_taTradeShTrend()
orders_infoEm = {}#use in AppEmulate e_taTrade()
orders_infoEmShTr = {}#use in AppEmulate e_taTradeShTrend()
eml_freezLong_GL = False #Flag for freez algoritms ShortTrend or MACD Up in AppEmulate
profitEm = 0 # profit for AppEmulate

#********** AppEmMargin
is_mrgTradeEm = False #working or not _mrgTradeEm
loop_AppEmMrg = 0 #loop Flag for AppEmMargin
loop_AppEmMrgShTr = 0 #loop Flag for AppEmMargin
orders_infoEmMrg = {}#use in AppEmMargin
orders_infoEmMrgShTr = {}#use in AppEmMargin
eml_freezShort_GL = False #Flag for freez algoritm ShortTrend or MACD Dn_in AppEmMargin

#********** oop
isMACD_GL = False #Flag for Crossed MACD algorithm
isSTrend_GL = True #Flag for fast Trend algorithm
isMRKT_GL = False #flag for buing by Market
isLMT_GL = True #flag for buing by LIMIT
nLMT_GL = 0 # +/- limit cost for Buy in base crypto
nLMT_MrgGL = 0 # +/- limit cost for Sell in base crypto
nLMTauto_GL = 0 # +/- limit in base crypto
nLMTautoDnLng_GL = 0
nLMTautoUpMrg_GL = 0 # +/- limit in base crypto
driveMode = 0 # 0 - Trade Emulation; 1 - Trade Real
#countTrade = 0
countPos = 0

#********** HSTREmulate
T = [0,0] # weight for Trend 0-when UP 1-when Down
buyPercentShTr_GL,buySLPercentShTr_GL = 0.16, 0.32 # buyXXX - for MARGIN trade
#sellPercentShTr_GL,sellSLPercentShTr_GL = 0.16, 0.32 #sellXXX - for LONG trade
#buyPercentCrdMACD_GL, buySLPercentCrdMACD_GL = 0.16,0.32 # buyXXX - for MARGIN trade
#sellPercentCrdMACD_GL,sellSLPercentCrdMACD_GL = 0.16,0.32 #sellXXX - for LONG trade
HSTR_countTrade = [1,2,3,4,5] #for Combo Box - Count Trade
HSTR_timeFrame = ['-1 hours','-2 hours','-3 hours','-4 hours','-5 hours','-6 hours','-7 hours','-8 hours','-12 hours']
HSTRLoop_GL = False #loop Flag for _HSTREm_alg
#sum_NegTrades_Gl = [0,0] #sum all negative trades in tables ([count][sum])
sum_NegTradesUp_Gl = [0,0] #sum all negative trades in tables when Up ([count][sum])
sum_NegTradesDn_Gl = [0,0] #sum all negative trades in tables when Down ([count][sum])
sum_PosTrades_Gl = [0,0] #sum all positive trades in tables
sum_eNegTrades_Gl = [0,0] #sum all emulation negative trades in tables ([count][sum])
sum_ePosTrades_Gl = [0,0] #sum all emulation positive trades in tables
timeFrame = '-1 hours'

candleCount = ['2','3','4','5']
limitUSD = ['1','2','3','4','5','6','7','8','9','10','15','20','25','30','35','40','45','50','70','90','110','120']
fastMoveCount = 0

#********** ta
bigUpPercent, bigDnPercent, bigUpPercentNow, bigDnPercentNow = 0,0,[0,0], [0,0] # set percent for big candles LINQ-> ta.py:429
#maxBdSubSetExtUp, maxBdSubSetExtDn = 0,0
Up3LastSet,Dn3LastSet,Up3LastNow, Dn3LastNow = 0.45,0.45,[0,0], [0,0]  # set percent size of body candle - for last 3 candels (short trend)
#setExtremPercent = 0.05
#setExtremPercentDn = 0.05
listPrntBigCandle = ['0.05','0.06','0.07','0.1','0.15','0.2','0.3','0.05=5%']
listPrntBigUpDn = ['0.15','0.25','0.35','0.45','0.55','0.65','0.75','0.25=0.25%'] # list for Big Up/Dn last Candle
listPrnt3LstBigUpDn = ['0.15','0.25','0.35','0.45','0.55','0.65','0.75','0.85','0.95','0.25=0.25%'] # list for 3 last Big Up/Dn last Candle
GrowOnPeriod, GrowOneBody, DnOnPeriod, DnOneBody = [], [], [], []


#orders_info_trailem = {}
setTrailStGL = {}
pairsGL, pairsGL_out, pairsGL_outMrg = [],[],[] #Список
#KlinePeriodGL = '' #period from ComboBox
symbolPairGL = ''
#first_balanceGL = 0
#first_balanceGL_app = 0

#taTradeLoop_GL = False #loop Flag for AppWork

#GMDLoop_GL = False #loop Flag for Get Market Data

USE_BNB_FEES = True
STOCK_FEE = 0.001  # Комиссия, которую берет биржа (0.001 = 0.1%)
SELLlng_LIFE_TIME_MIN = 90
HSTR_LIFE_TIME_MIN = 20
SELLshrt_LIFE_TIME_MIN = 3
BUYshrt_LIFE_TIME_MIN = 90
BUYlng_LIFE_TIME_MIN = 3
BS_LIFE_TIME_MIN = 15 # for buy or sell(short)

KLINES_LIMITS = 0
POINTS_TO_ENTER = 3
USE_OPEN_CANDLES = True
#TIMEFRAME = "1h"
'''
    Допустимые интервалы:
    •    1m     // 1 минута
    •    3m     // 3 минуты
    •    5m    // 5 минут
    •    15m  // 15 минут
    •    30m    // 30 минут
    •    1h    // 1 час
    •    2h    // 2 часа
    •    4h    // 4 часа
    •    6h    // 6 часов
    •    8h    // 8 часов
    •    12h    // 12 часов
    •    1d    // 1 день
    •    3d    // 3 дня
    •    1w    // 1 неделя
    •    1M    // 1 месяц
'''
macd_prev = 0 #previous value MACD
macdH_prev = 0 #previous value for MACD Histogram
maFast_prev = 0
maSlow_prev = 0
# Подключаем логирование
logging.basicConfig(
    format="%(asctime)s [%(levelname)-5.5s] %(message)s",
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler("{path}/logs/{fname}.log".format(path=os.path.dirname(os.path.abspath(__file__)), fname="binance")),
        logging.StreamHandler()
    ])
log = logging.getLogger('')

ORDER_STATUS = ['NEW', 'PARTIALLY_FILLED', 'PARTIALLY_FILLED', 'FILLED', 'CANCELED', 'PENDING_CANCEL', 'REJECTED', 'EXPIRED']


# cfTXT = 'YYYYYYYYYYYY'
# [
#   [
#     1499040000000,      // Open time
#     "0.01634790",       // Open
#     "0.80000000",       // High
#     "0.01575800",       // Low
#     "0.01577100",       // Close
#     "148976.11427815",  // Volume in base currency???
#     1499644799999,      // Close time
#     "2434.19055334",    // Quote asset volume
#     308,                // Number of trades
#     "1756.87402397",    // Taker buy base asset volume
#     "28.46694368",      // Taker buy quote asset volume
#     "17928899.62484339" // Can be ignored
#   ]
# ]

# {
#   "symbol": "BTCUSDT",
#   "orderId": 28,
#   "orderListId": -1, //Unless OCO, value will be -1
#   "clientOrderId": "6gCrw2kRUAF9CvJDGP16IP",
#   "transactTime": 1507725176595,
#   "price": "0.00000000",
#   "origQty": "10.00000000",
#   "executedQty": "10.00000000",
#   "cummulativeQuoteQty": "10.00000000",
#   "status": "FILLED",
#   "timeInForce": "GTC",
#   "type": "MARKET",
#   "side": "SELL"
# }