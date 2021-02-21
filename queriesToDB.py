import configGlb as cnf
from datetime import datetime
import time

def test(cursor, conn, buy_order_id, sell_order_id, amount, price, income,sl):
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! update_buy_order_emMRG !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    force_buy_ = price if sl == 0 else 0 #if Stop loss
    price_ = price if sl == 1 else 0 #if not Stop loss
    try:
        cursor.execute(
            """
              UPDATE ordersEmMrg
              SET
                order_type = 'buy',
                buy_created = :dt1,
                buy_order_id = :buy_order_id,              
                buy_amount = :buy_amount,
                income = :income,
                buy_price = :buy_price,
                force_buy = :force_buy
              WHERE
                sell_order_id = :sell_order_id
        
            """, {
                'dt1': datetime.fromtimestamp(),
                'buy_order_id': buy_order_id,
                'buy_amount': amount,
                'income': income,
                'sell_order_id': sell_order_id,
                'buy_price': price_,
                'force_buy': force_buy_
            }
        )
        conn.commit()
        cnf.testSQLiteGlb = True
        print('commit Good!!!!! ')
    except conn.Error:
        #cnf.testSQLiteGlb = False
        print('conn.Error: ' + str(conn.Error) + ';  testSQLiteGlb: ' + str(cnf.longSQLiteGlb) + '\n')


def make_initial_portf(cursor):
    # Если не существует таблиц, их нужно создать (первый запуск)
    crt_portfolio = """
     create table if not exists
       portfolio (
          dt_create DATETIME NULL,
          balance_all REAL NULL,
          balance_base REAL NULL,
          income REAL NULL
          );
    """
    cursor.execute(crt_portfolio)

def add_record_portfolio(cursor,conn,dt,b_all,b_base):
    cursor.execute(
        """
          INSERT INTO portfolio(
              dt_create,
              balance_all, 
              balance_base
          ) Values (
              :dt_create,
              :balance_all, 
              :balance_base
          )
        """, {
            'dt_create': dt,
            'balance_all': b_all,
            'balance_base': b_base
        }
    )
    conn.commit()

def get_rec_portfolio(cursor):
    crt_portfolio = """
            SELECT * FROM portfolio ORDER BY dt_create DESC LIMIT 1
    """
    record = []
    for row in cursor.execute(crt_portfolio):
        record = row
    return record

def get_rec_ordersTa(cursor,d,f):
#           SELECT buy_created,strftime('%Y',buy_created) FROM ordersTa;
    mnf = "'" + d + "')"
    ordersTa = "SELECT * FROM ordersTa WHERE sell_finished >= datetime('now'," + mnf
    ordersTaShTr = "SELECT * FROM ordersTaShTr WHERE sell_finished >= datetime('now'," + mnf

    ordersMrg = "SELECT * FROM ordersMrg WHERE buy_finished >= datetime('now'," + mnf
    ordersMrgShTr = "SELECT * FROM ordersMrgShTr WHERE buy_finished >= datetime('now'," + mnf

    ordersEmTa = "SELECT * FROM ordersEmTa WHERE buy_created >= datetime('now'," + mnf
    ordersEmMrg = "SELECT * FROM ordersEmMrg WHERE buy_created >= datetime('now'," + mnf

    order_exec = ordersTa if f == 1 else ordersEmTa
    order_execShort = ordersMrg if f == 1 else ordersEmMrg
    order_execShTr = ordersTaShTr
    order_execMrgShTr = ordersMrgShTr
    record = []
    record2 = []
    recordShTr = []
    recordMrgShTr = []
    for row in cursor.execute(order_exec):
        record.append(row)
    for row in cursor.execute(order_execShort):
        record2.append(row)
    for row in cursor.execute(order_execShTr):
        recordShTr.append(row)
    for row in cursor.execute(order_execMrgShTr):
        recordMrgShTr.append(row)

    return record, record2, recordShTr,recordMrgShTr

######################### REAL TRADE ##################################
def make_initial_table_MRG(cursor):
    orders_mrg = """
                  create table if not exists
                    ordersMrg (
                      order_type TEXT,
                      order_pair TEXT,
                      order_side TEXT,
                      sell_order_id NUMERIC NULL,
                      sell_amount REAL NULL,
                      sell_price REAL NULL,
                      sell_created DATETIME NULL,
                      sell_finished DATETIME NULL,
                      force_sell INT DEFAULT 0,
                      sell_verified INT DEFAULT 0,

                      buy_order_id NUMERIC,
                      buy_amount REAL,
                      buy_price REAL,
                      buy_created DATETIME,
                      buy_finished DATETIME NULL,
                      sell_cancelled DATETIME NULL,
                      buy_verified INT DEFAULT 0,

                      panic_fee REAL NULL, 
                      income REAL NULL,                     
                      balance REAL NULL,
                      profit REAL DEFAULT 0                                        
                    );
                """
    cursor.execute(orders_mrg)

def get_open_orders_MRG(cursor):
    orders_mrg = """
            SELECT 
             sell_order_id
            ,order_type
            ,order_pair
            ,buy_order_id
            ,sell_amount
            ,sell_price
            ,balance
            ,sell_verified
            ,profit
            ,panic_fee
            ,sell_finished
            FROM
              ordersMrg
            WHERE
              order_type='sell'
    """
    cnf.orders_infoMrgMACD = {}

    for row in cursor.execute(orders_mrg):
        cnf.orders_infoMrgMACD[str(row[0])] = dict(row)
    return cnf.orders_infoMrgMACD


def update_sell_MRG(cursor, conn, order_id, rate):
    cursor.execute(
        """
          UPDATE ordersMrg
          SET
            sell_verified=1,
            sell_price = :sell_price,
            sell_finished  = :dt
          WHERE
            sell_order_id = :sell_order_id
        """, {
            'sell_order_id': order_id,
            'sell_price': rate,
            'dt': datetime.fromtimestamp(int(time.time()))
        }
    )
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! update_sell_MRG !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    conn.commit()

def update_sell_Cancel_MRG(cursor, conn, order_id):
    cnf.shortSQLiteGlb = False
    try:
        cursor.execute(
            """
              UPDATE ordersMrg
              SET 
                order_type='buy',
                sell_cancelled = :dt  
              WHERE sell_order_id = :sell_order_id
            """, {
                'sell_order_id':order_id,
                'dt': datetime.fromtimestamp(int(time.time()))
            }
        )
        conn.commit()
        cnf.shortSQLiteGlb = True
    except conn.Error:
        print('update_sell_Cancel_MRG().... conn.Error: ' + str(conn.Error) + '\n')

def update_buy_lmt_MRG(cursor, conn, sell_order_id, buy_order_id):
    q = """
         UPDATE ordersMrg SET buy_order_id={so} WHERE sell_order_id={boi}
     """.format(so=buy_order_id, boi=sell_order_id)
    cursor.execute(q)
    conn.commit()

def add_new_order_SELL_MRG(cursor, conn, pair_name, orderID, my_amount, my_need_price, spend_sum, prf, pf, os):
    cnf.shortSQLiteGlb = False
    try:
        cursor.execute(
            """
              INSERT INTO ordersMrg(
                  order_type,
                  order_pair,
                  sell_order_id,
                  sell_amount,
                  sell_price,
                  sell_created,
                  balance,
                  profit,
                  panic_fee,
                  order_side
        
              ) Values (
                'sell',
                :order_pair,
                :sell_order_id,
                :sell_amount,
                :sell_price,
                :sell_created,
                :balance,
                :profit,
                :panic_fee,
                :order_side
              )
            """, {
                'order_pair': pair_name,
                'sell_order_id': orderID,
                'sell_amount': my_amount,
                'sell_price': my_need_price,
                'sell_created': datetime.fromtimestamp(int(time.time())),
                'balance': spend_sum,
                'profit': prf,
                'panic_fee': pf,
                'order_side': os
            }
        )
        conn.commit()
        cnf.shortSQLiteGlb = True
    except conn.Error:
        print('add_new_order_SELL_MRG().... conn.Error: ' + str(conn.Error) + '\n')

def store_buy_order_MRG(cursor, conn, buy_order_id, sell_order_id, amount):
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! store_buy_order_MRG!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    cnf.shortSQLiteGlbBuy = False
    try:
        cursor.execute(
            """
              UPDATE ordersMrg
              SET
                buy_created = :dt1,
                buy_order_id = :buy_order_id,              
                buy_amount = :buy_amount
              WHERE
                sell_order_id = :sell_order_id
        
            """, {
                'dt1': datetime.fromtimestamp(int(time.time())),
                'buy_order_id': buy_order_id,
                'buy_amount': amount,
                'sell_order_id': sell_order_id
            }
        )
        conn.commit()
        cnf.shortSQLiteGlbBuy = True
    except conn.Error:
        print('store_buy_order_MRG().... conn.Error: ' + str(conn.Error) + '\n')

def update_buy_order_MRG(cursor, conn, sell_orderID, rate, income,f):
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! update_buy_order_MRG !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    cnf.shortSQLiteGlbBuy = False
    try:
        if f == 0: #if stop loss(f=0) then fsell
            fsell = rate
            cnf.appMrgProfit_GL[2] += 1 # increase count of trade
            cnf.appMrgProfit_GL[3] += income # sum profit of trade
        else:
            fsell = 0
            cnf.appMrgProfit_GL[0] += 1 # increase count of trade
            cnf.appMrgProfit_GL[1] += income # sum profit of trade
        cursor.execute(
            """
              UPDATE ordersMrg
              SET
                order_type='buy',
                buy_verified=1,
                buy_price = :buy_price,
                buy_finished  = :dt,
                income = :income,
                force_sell = :force_sell
              WHERE
                sell_order_id = :sell_order_id
            """, {
                'sell_order_id': sell_orderID,
                'buy_price':rate,
                'dt': datetime.fromtimestamp(int(time.time())),
                'income': income,
                'force_sell': fsell
            }
        )
        conn.commit()
        cnf.shortSQLiteGlbBuy = True
    except conn.Error:
        print('update_buy_order_MRG().... conn.Error: ' + str(conn.Error) + '\n')



def make_initial_table_MRG_ShTr(cursor):
    orders_mrg = """
                  create table if not exists
                    ordersMrgShTr (
                      order_type TEXT,
                      order_pair TEXT,
                      order_side TEXT,
                      sell_order_id NUMERIC NULL,
                      sell_amount REAL NULL,
                      sell_price REAL NULL,
                      sell_created DATETIME NULL,
                      sell_finished DATETIME NULL,
                      force_sell INT DEFAULT 0,
                      sell_verified INT DEFAULT 0,

                      buy_order_id NUMERIC,
                      buy_amount REAL,
                      buy_price REAL,
                      buy_created DATETIME,
                      buy_finished DATETIME NULL,
                      buy_cancelled DATETIME NULL,
                      buy_verified INT DEFAULT 0,

                      panic_fee REAL NULL, 
                      income REAL NULL,                     
                      balance REAL NULL,
                      profit REAL DEFAULT 0                                        
                    );
                """
    cursor.execute(orders_mrg)

def get_rec_4Tables(cursor, hours):
    h = "'" + hours + "','localtime')"
    ordersTa = "SELECT * FROM ordersTa WHERE sell_finished >= datetime('now'," + h
    ordersMrg = "SELECT * FROM ordersMrg WHERE buy_finished >= datetime('now'," + h
    ordersTaShTr = "SELECT * FROM ordersTaShTr WHERE sell_finished >= datetime('now'," + h
    ordersMrgShTr = "SELECT * FROM ordersMrgShTr WHERE buy_finished >= datetime('now'," + h
    rec_ordersTa, rec_ordersMrg, rec_ordersTaShTr, rec_ordersMrgShTr = [],[],[],[]
   # print('ordersEmMrg: ' + str(ordersEmMrg))

    for row in cursor.execute(ordersTa):
        rec_ordersTa.append(row)
    for row in cursor.execute(ordersMrg):
        rec_ordersMrg.append(row)
    for row in cursor.execute(ordersTaShTr):
        rec_ordersTaShTr.append(row)
    for row in cursor.execute(ordersMrgShTr):
        rec_ordersMrgShTr.append(row)
    dtn = datetime.now()
    # print('get_rec_4Tables() datetime now/hours ' + str(dtn) + '/' + str(dtn.hour))
    # for list in rec_ordersTaShTr:
    #     for item in list:
    #        print(": ", item)
    return rec_ordersTa,rec_ordersMrg, rec_ordersTaShTr, rec_ordersMrgShTr

def get_rec_4TablesEm(cursor, hours):
    h = "'" + hours + "')"
    ordersEmTa = "SELECT * FROM ordersEmTa WHERE sell_created >= datetime('now'," + h
    ordersEmMrg = "SELECT * FROM ordersEmMrg WHERE buy_created >= datetime('now'," + h
    ordersEmTaShTr = "SELECT * FROM ordersEmTaShTr WHERE sell_created >= datetime('now'," + h
    ordersEmMrgShTr = "SELECT * FROM ordersEmMrgShTr WHERE buy_created >= datetime('now'," + h
    rec_ordersTa, rec_ordersMrg, rec_ordersTaShTr, rec_ordersMrgShTr = [],[],[],[]


    for row in cursor.execute(ordersEmTa):
        rec_ordersTa.append(row)
    for row in cursor.execute(ordersEmMrg):
        rec_ordersMrg.append(row)
    for row in cursor.execute(ordersEmTaShTr):
        rec_ordersTaShTr.append(row)
    for row in cursor.execute(ordersEmMrgShTr):
        rec_ordersMrgShTr.append(row)

    #print('datetime now: ' + str(datetime.now()))
    # for list in rec_ordersMrg:
    #     for item in list:
    #         print("ordersEmMrg:  ", item)
    return rec_ordersTa,rec_ordersMrg, rec_ordersTaShTr, rec_ordersMrgShTr

def get_open_orders_MRG_ShTr(cursor):
    orders_mrg = """
            SELECT 
             sell_order_id
            ,order_type
            ,order_pair
            ,buy_order_id
            ,sell_amount
            ,sell_price
            ,balance
            ,profit
            ,panic_fee
            ,sell_verified
            ,sell_finished
            FROM
              ordersMrgShTr
            WHERE
              order_type='sell'
    """
    cnf.orders_infoMrgShTr = {}
    for row in cursor.execute(orders_mrg):
        cnf.orders_infoMrgShTr[str(row[0])] = dict(row)
    return cnf.orders_infoMrgShTr

def add_new_order_SELL_MRG_ShTr(cursor, conn, pname, orderID, my_amount, sel_price, spend_sum, prf, pf,os):
    cnf.shortSQLiteGlb = False
    try:
        cursor.execute(
            """
              INSERT INTO ordersMrgShTr(
                  order_type,
                  order_pair,
                  sell_order_id,
                  sell_amount,
                  sell_price,
                  sell_created,
                  balance,
                  profit,
                  panic_fee,
                  order_side
        
              ) Values (
                'sell',
                :order_pair,
                :sell_order_id,
                :sell_amount,
                :sell_price,
                :sell_created,
                :balance,
                :profit,
                :panic_fee,
                :order_side
              )
            """, {
                'order_pair': pname,
                'sell_order_id': orderID,
                'sell_amount': my_amount,
                'sell_price': sel_price,
                'sell_created': datetime.fromtimestamp(int(time.time())),
                'balance': spend_sum,
                'profit': prf,
                'panic_fee': pf,
                'order_side': os
            }
        )
        conn.commit()
        cnf.shortSQLiteGlb = True
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ordersMrgShTr Succes !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    except conn.Error:
        print('add_new_order_SELL_appTA_ShTr()... conn.Error: ' + str(conn.Error) + '\n')

def update_sell_MRG_ShTr(cursor, conn, order_id, rate):
    cursor.execute(
        """
          UPDATE ordersMrgShTr
          SET
            order_type='sell',
            sell_verified=1,
            sell_price = :sell_price,
            sell_finished  = :dt
          WHERE
            sell_order_id = :sell_order_id
        """, {
            'sell_order_id': order_id,
            'sell_price': rate,
            'dt': datetime.fromtimestamp(int(time.time()))
        }
    )
    conn.commit()

def update_sell_Cancel_MRG_ShTr(cursor, conn, order_id):
    cnf.shortSQLiteGlb = False
    try:
        cursor.execute(
            """
              UPDATE ordersMrgShTr
              SET 
                order_type='buy',
                sell_cancelled = :dt  
              WHERE 
                sell_order_id = :sell_order_id
            """, {
                'sell_order_id':order_id,
                'dt': datetime.fromtimestamp(int(time.time()))
            }
        )

        cursor.execute(
            """
              UPDATE ordersTAShTr 
              SET 
                order_type='sell',
                buy_cancelled = :dt  
              WHERE buy_order_id = :buy_order_id
            """, {
                'buy_order_id':order_id,
                'dt': datetime.fromtimestamp(int(time.time()))
            }
        )
        conn.commit()
        cnf.shortSQLiteGlb = True
    except conn.Error:
        print('update_sell_Cancel_MRG_ShTr().... conn.Error: ' + str(conn.Error) + '\n')

def store_buy_order_MRG_ShTr(cursor, conn, buy_order_id, sell_order_id, amount):
    cnf.shortSQLiteGlbBuy = False
    try:
        cursor.execute(
            """
              UPDATE ordersMrgShTr
              SET
                buy_created = :dt1,
                buy_order_id = :buy_order_id,              
                buy_amount = :buy_amount
              WHERE
                sell_order_id = :sell_order_id
        
            """, {
                'dt1': datetime.fromtimestamp(int(time.time())),
                'buy_order_id': buy_order_id,
                'buy_amount': amount,
                'sell_order_id': sell_order_id
            }
        )
        conn.commit()
        cnf.shortSQLiteGlbBuy = True
    except conn.Error:
        print('astore_buy_order_MRG_ShTr().... conn.Error: ' + str(conn.Error) + '\n')

def update_buy_order_MRG_ShTr(cursor, conn, sell_orderID, rate, income,f):
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! update_buy_order_MRG_ShTr !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    cnf.shortSQLiteGlb = False
    try:
        if f == 0: #if stop loss(f=0) then fsell
            fsell = rate
            cnf.appMrgProfit_GL[2] += 1 # increase count of trade
            cnf.appMrgProfit_GL[3] += income # sum profit of trade
        else:
            fsell = 0
            cnf.appMrgProfit_GL[0] += 1 # increase count of trade
            cnf.appMrgProfit_GL[1] += income # sum profit of trade
        cursor.execute(
            """
              UPDATE ordersMrgShTr
              SET
                order_type='buy',
                buy_verified=1,
                buy_price = :buy_price,
                buy_finished  = :dt,
                income = :income,
                force_sell = :force_sell
              WHERE
                sell_order_id = :sell_order_id
            """, {
                'sell_order_id': sell_orderID,
                'buy_price':rate,
                'dt': datetime.fromtimestamp(int(time.time())),
                'income': income,
                'force_sell': fsell
            }
        )
        conn.commit()
        cnf.shortSQLiteGlb = True
    except conn.Error:
        print('update_buy_order_MRG_ShTrr().... conn.Error: ' + str(conn.Error) + '\n')

# def update_sell_lmt_MRG_ShTr(cursor, conn, sell_order_id, buy_order_id):
#     q = """
#          UPDATE ordersMrgShTr SET buy_order_id={so} WHERE sell_order_id={boi}
#      """.format(so=buy_order_id, boi=sell_order_id)
#     cursor.execute(q)
#     conn.commit()



def make_initial_tables_appTA(cursor):
    # Если не существует таблиц, их нужно создать (первый запуск)
    orders_q = """
                  create table if not exists
                    ordersTA (
                      order_type TEXT,
                      order_pair TEXT,
                      order_side TEXT,
                      buy_order_id NUMERIC,
                      buy_amount REAL,
                      buy_price REAL,
                      buy_created DATETIME,
                      buy_finished DATETIME NULL,
                      buy_cancelled DATETIME NULL,
                      buy_verified INT DEFAULT 0,

                      sell_order_id NUMERIC NULL,
                      sell_amount REAL NULL,
                      sell_price REAL NULL,
                      sell_created DATETIME NULL,
                      sell_finished DATETIME NULL,
                      force_sell INT DEFAULT 0,
                      sell_verified INT DEFAULT 0,
                      income REAL NULL,
                      profit REAL NULL,
                      panic_fee REAL NULL
                    );
                """
    cursor.execute(orders_q)

def get_open_orders_appTA(cursor):
    orders_q = """
                    SELECT
                        buy_order_id
                      , order_type
                      , order_side
                      , order_pair
                      , sell_order_id
                      , sell_price
                      , buy_amount
                      , buy_price
                      , buy_verified
                      , buy_created
                      , profit
                      , panic_fee
                    FROM
                      ordersTA
                    WHERE
                      order_type='buy'
                """
    cnf.orders_infoMACD = {}

    for row in cursor.execute(orders_q):
        cnf.orders_infoMACD[str(row[0])] = dict(row)
    return cnf.orders_infoMACD
# def get_db_running_pairs_appTA(cursor):
#     orders_q = """
#         SELECT
#           distinct(order_pair) pair
#         FROM
#           ordersTA
#         WHERE
#           buy_cancelled IS NULL AND CASE WHEN order_type='buy' THEN buy_finished IS NULL ELSE sell_finished IS NULL END
#     """
#     res = []
#     for row in cursor.execute(orders_q):
#         res.append(row[0])
#     return res
def add_new_order_buy_appTA(cursor, conn, pair_name, order_id, amount, price, prf,pf,selLMT,os):
    cnf.longSQLiteGlb = False
    try:
        cursor.execute(
            """
              INSERT INTO ordersTA(
                  order_type,
                  order_pair,
                  buy_order_id,
                  buy_amount,
                  buy_price,
                  buy_created,
                  profit,
                  panic_fee,
                  sell_price,
                  order_side
        
              ) Values (
                'buy',
                :order_pair,
                :order_id,
                :buy_order_amount,
                :buy_initial_price,
                :dt,
                :profit,
                :panic_fee,
                :sell_price,
                :order_side
              )
            """, {
                'order_pair': pair_name,
                'order_id': order_id,
                'buy_order_amount': amount,
                'buy_initial_price': price,
                'dt': datetime.fromtimestamp(int(time.time())),
                'profit':prf,
                'panic_fee': pf,
                'sell_price': selLMT,
                'order_side': os
            }
        )
        conn.commit()
        cnf.longSQLiteGlb = True
    except conn.Error:
        print('add_new_order_buy_appTA().... conn.Error: ' + str(conn.Error) + '\n')


# Update table ordersTA after buing(long) - use in AppWork
def update_buy_rate_appTA(cursor, conn, order_id, rate):
    cursor.execute(
        """
          UPDATE ordersTA 
          SET 
            buy_verified=1, 
            buy_price = :buy_price, 
            buy_finished = :dt  
          WHERE buy_order_id = :bOrderID
        """, {
            'bOrderID': order_id,
            'buy_price': rate,
            'dt': datetime.fromtimestamp(int(time.time()))
        }
    )
    conn.commit()
# Update table ordersTA after exit buing(long) - use in AppWork
# def get_dtBuy_appTA(cursor,order_id):
#     # orders_q = """
#     #                 SELECT
#     #                   buy_created
#     #                 FROM
#     #                   ordersTA
#     #                 WHERE
#     #                   buy_order_id = order_id
#     #             """
#     q = """
#          SELECT strftime('%s',buy_created) FROM ordersTA WHERE buy_order_id={order_id}
#      """.format(order_id=order_id)
#     #dt = []
#
#     for row in cursor.execute(q):
#         #dt.append(row[0])
#         dt = row[0]
#     return dt
# def update_buy_exit_appTA(cursor, conn, buy_order_id, dt):
#     q = """
#         UPDATE ordersTA SET buy_verified=0, buy_cancelled={dt}  WHERE buy_order_id={order_id}
#     """.format(dt=dt,order_id=buy_order_id)
#     cursor.execute(q)
#     conn.commit()
def store_sell_order_appTA(cursor, conn, buy_order_id, sell_order_id, amount, prf):
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! store_sell_order_appTA !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    cnf.longSQLiteGlbSell = False
    try:
        cursor.execute(
            """
              UPDATE ordersTA
              SET
                sell_order_id = :sell_order_id,
                sell_created = :dt2,
                sell_amount = :sell_amount,
                profit = :profit
              WHERE
                buy_order_id = :buy_order_id
        
            """, {
                'buy_order_id': buy_order_id,
                'sell_order_id': sell_order_id,
                'dt2': datetime.fromtimestamp(int(time.time())),
                'sell_amount': amount,
                'profit': prf
            }
        )
        conn.commit()
        cnf.longSQLiteGlbSell = True
    except conn.Error:
        print('store_sell_order_appTA().... conn.Error: ' + str(conn.Error) + '\n')

def update_sell_rate_appTA(cursor, conn, buy_order_id, rate,income,f):
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! update_sell_rate_appTA !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    cnf.longSQLiteGlbSell = False
    if f == 0: #if stop loss(f=0) then fsell
        fsell = rate
        cnf.appProfit_GL[2] += 1 # increase count of trade
        cnf.appProfit_GL[3] += income # sum profit of trade
    else:
        fsell = 0
        cnf.appProfit_GL[0] += 1 # increase count of trade
        cnf.appProfit_GL[1] += income # sum profit of trade
    try:
        cursor.execute(
            """
              UPDATE ordersTA
              SET
                order_type = 'sell',
                sell_verified=1,
                sell_price = :sell_price,
                sell_finished  = :dt,
                income = :income,
                force_sell = :force_sell
              WHERE
                buy_order_id = :buy_order_id
            """, {
                'buy_order_id': buy_order_id,
                'sell_price': rate,
                'dt': datetime.fromtimestamp(int(time.time())),
                'income': income,
                'force_sell': fsell
            }
            )
        conn.commit()
        cnf.longSQLiteGlbSell = True
    except conn.Error:
        print('update_sell_rate_appTA().... conn.Error: ' + str(conn.Error) + '\n')

def update_sell_lmt_appTA(cursor, conn, buy_order_id,sell_order_id):
    cnf.longSQLiteGlbSell = False
    q = """
         UPDATE ordersTA SET sell_order_id={so} WHERE buy_order_id={boi}
     """.format(so=sell_order_id, boi=buy_order_id)
    try:
        cursor.execute(q)
        conn.commit()
        cnf.longSQLiteGlbSell = True
    except conn.Error:
        print('update_sell_lmt_appTA().... conn.Error: ' + str(conn.Error) + '\n')

def update_buy_Cancel_appTA(cursor, conn, order_id):
    cnf.longSQLiteGlb = False
    try:
        cursor.execute(
            """
              UPDATE ordersTA
              SET 
                order_type='sell',
                buy_cancelled = :dt  
              WHERE buy_order_id = :buy_order_id
            """, {
                'buy_order_id':order_id,
                'dt': datetime.fromtimestamp(int(time.time()))
            }
        )
        conn.commit()
        cnf.longSQLiteGlb = True
    except conn.Error:
        print('update_buy_Cancel_appTA().... conn.Error: ' + str(conn.Error) + '\n')
def update_sell_Cancel_appTA(cursor, conn, order_id):
    cursor.execute(
        """
          UPDATE ordersTA
          SET 
            sell_order_id=0,
            sell_created = NULL  
          WHERE sell_order_id = :sellOrderId
        """, {
            'sellOrderId':order_id
        }
    )
    conn.commit()


###################### Real Trade tables for Short Trend alg #######
def make_initial_tables_appTA_ShTr(cursor):
    # Если не существует таблиц, их нужно создать (первый запуск)
    orders_q = """
                  create table if not exists
                    ordersTAShTr (
                      order_type TEXT,
                      order_pair TEXT,
                      order_side TEXT,
                      buy_order_id NUMERIC,
                      buy_amount REAL,
                      buy_price REAL,
                      buy_created DATETIME,
                      buy_finished DATETIME NULL,
                      buy_cancelled DATETIME NULL,
                      buy_verified INT DEFAULT 0,

                      sell_order_id NUMERIC NULL,
                      sell_amount REAL NULL,
                      sell_price REAL NULL,
                      sell_created DATETIME NULL,
                      sell_finished DATETIME NULL,
                      force_sell INT DEFAULT 0,
                      sell_verified INT DEFAULT 0,
                      income REAL NULL,
                      profit REAL NULL,
                      panic_fee REAL NULL
                    );
                """
    cursor.execute(orders_q)

def get_open_orders_appTA_ShTr(cursor):
    orders_q = """
                    SELECT
                        buy_order_id
                      ,order_type
                      ,order_pair
                      ,sell_order_id
                      ,sell_price
                      ,buy_amount
                      ,buy_price
                      ,buy_verified
                      ,buy_created
                      ,profit
                      ,panic_fee
                    FROM
                      ordersTAShTr
                    WHERE
                      order_type='buy'
                """
    cnf.orders_infoShTr = {}
    for row in cursor.execute(orders_q):
        cnf.orders_infoShTr[str(row[0])] = dict(row)
        return cnf.orders_infoShTr

# def get_running_pairs_appTA_ShTr(cursor):
#     # return only different values
#     orders_q = """
#         SELECT
#            buy_order_id
#           ,sell_order_id
#         FROM
#           ordersTAShTr
#         WHERE
#           buy_verified IS NULL
#     """
#     res = []
#     for row in cursor.execute(orders_q):
#         res.append(row[0])
#     return res
# def get_hang_pairs_appTA_ShTr(cursor):
#
#     orders_q = """
#         SELECT
#           distinct(order_pair) pair
#         FROM
#           ordersTAShTr
#         WHERE
#           buy_cancelled IS NULL AND CASE WHEN order_type='buy' THEN buy_finished IS NULL ELSE sell_finished IS NULL END
#     """
#     res = []
#     for row in cursor.execute(orders_q):
#         res.append(row[0])
#     return res
def add_new_order_buy_appTA_ShTr(cursor, conn, pair_name, order_id, amount, price, prf,pf,selLMT,os):
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! add_new_order_buy_appTA_ShTr!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    cnf.longSQLiteGlb = False
    try:
        cursor.execute(
            """
              INSERT INTO ordersTAShTr(
                  order_type,
                  order_pair,
                  buy_order_id,
                  buy_amount,
                  buy_price,
                  buy_created,
                  profit,
                  panic_fee,
                  sell_price,
                  order_side

              ) Values (
                'buy',
                :order_pair,
                :order_id,
                :buy_order_amount,
                :buy_initial_price,
                :dt,
                :profit,
                :panic_fee,
                :sell_price,
                :order_side
              )
            """, {
                'order_pair': pair_name,
                'order_id': order_id,
                'buy_order_amount': amount,
                'buy_initial_price': price,
                'dt': datetime.fromtimestamp(int(time.time())),
                'profit': prf,
                'panic_fee': pf,
                'sell_price': selLMT,
                'order_side': os
            }
        )
        conn.commit()
        cnf.longSQLiteGlb = True
    except conn.Error:
        print('add_new_order_buy_appTA_ShTr().... conn.Error: ' + str(conn.Error) + '\n')

def store_sell_order_appTA_ShTr(cursor, conn, buy_order_id, sell_order_id, amount, prf):
    cnf.longSQLiteGlbSell = False
    try:
        cursor.execute(
            """
              UPDATE ordersTAShTr
              SET
                buy_finished = :dt1,
                sell_order_id = :sell_order_id,
                sell_created = :dt2,
                sell_amount = :sell_amount,
                profit = :profit
              WHERE
                buy_order_id = :buy_order_id
        
            """, {
                'dt1': datetime.fromtimestamp(int(time.time())),
                'buy_order_id': buy_order_id,
                'sell_order_id': sell_order_id,
                'dt2': datetime.fromtimestamp(int(time.time())),
                'sell_amount': amount,
                'profit': prf
            }
        )
        conn.commit()
        cnf.longSQLiteGlbSell = True
    except conn.Error:
        print('add_new_order_buy_appTA_ShTr().... conn.Error: ' + str(conn.Error) + '\n')

def update_sell_rate_appTA_ShTr(cursor, conn, buy_orderID, rate, income,f):
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! update_sell_rate_appTA_ShTr !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    cnf.longSQLiteGlbSell = False
    if f == 0: #if stop loss(f=0) then fsell
        fsell = rate
        cnf.appProfit_GL[2] += 1 # increase count of trade
        cnf.appProfit_GL[3] += income # sum profit of trade
    else:
        fsell = 0
        cnf.appProfit_GL[0] += 1 # increase count of trade
        cnf.appProfit_GL[1] += income # sum profit of trade
    try:
        cursor.execute(
            """
              UPDATE ordersTAShTr
              SET
                order_type='sell',
                sell_verified=1,
                sell_price = :sell_price,
                sell_finished  = :dt,
                income = :income,
                force_sell = :force_sell
              WHERE
                buy_order_id = :buy_order_id
            """, {
                'buy_order_id': buy_orderID,
                'sell_price': rate,
                'dt': datetime.fromtimestamp(int(time.time())),
                'income': income,
                'force_sell': fsell
            }
        )
        conn.commit()
        cnf.longSQLiteGlbSell = True
    except conn.Error:
        print('update_sell_rate_appTA_ShTr().... conn.Error: ' + str(conn.Error) + '\n')
def update_buy_rate_appTA_ShTr(cursor, conn, order_id, rate):
    cursor.execute(
        """
          UPDATE ordersTAShTr 
          SET 
            buy_verified=1, 
            buy_price = :buy_price, 
            buy_finished = :dt  
          WHERE buy_order_id = :bOrderID
        """, {
            'bOrderID': order_id,
            'buy_price': rate,
            'dt': datetime.fromtimestamp(int(time.time()))

        }
    )
    conn.commit()

def update_buy_Cancel_appTA_ShTr(cursor, conn, order_id):
    cnf.longSQLiteGlb = False
    try:
        cursor.execute(
            """
              UPDATE ordersTAShTr 
              SET 
                order_type='sell',
                buy_cancelled = :dt  
              WHERE buy_order_id = :buy_order_id
            """, {
                'buy_order_id':order_id,
                'dt': datetime.fromtimestamp(int(time.time()))
            }
        )
        conn.commit()
        cnf.longSQLiteGlb = True
    except conn.Error:
        print('update_buy_Cancel_appTA_ShTr().... conn.Error: ' + str(conn.Error) + '\n')


######################### EMULATUION TRADE ############################
def make_initial_table_emMRG(cursor):
    # Если не существует таблиц, их нужно создать (первый запуск)
    orders_em_mrg = """
                  create table if not exists
                    ordersEmMrg (
                      sell_order_id NUMERIC NULL,
                      sell_amount REAL NULL,
                      sell_price REAL NULL,
                      sell_created DATETIME NULL,
                      sell_finished DATETIME NULL,
                      order_type TEXT,
                      order_pair TEXT,
                      order_side TEXT,
                      buy_order_id NUMERIC,
                      buy_amount REAL,
                      buy_price REAL,
                      buy_created DATETIME,
                      force_buy INT DEFAULT 0,

                      panic_fee REAL NULL, 
                      income REAL NULL,                     
                      balance REAL NULL,
                      balance_emta REAL NULL,
                      profit REAL DEFAULT 0                                        
                    );
                """
    cursor.execute(orders_em_mrg)

def get_open_orders_emMRG(cursor,pair):
    orders_em_mrg = """
             SELECT sell_order_id,order_type,order_pair,buy_order_id,sell_amount,sell_price,balance,profit,panic_fee,sell_price,sell_created 
             FROM ordersEmMrg WHERE order_type=? AND buy_order_id IS NULL AND order_pair=?
         """
        #.format(pr=pair)

    # orders_em_mrg = """
    #         SELECT
    #          sell_order_id
    #         ,order_type
    #         ,order_pair
    #         ,buy_order_id
    #         ,sell_amount
    #         ,sell_price
    #         ,sell_created
    #         ,balance
    #         ,profit
    #         ,panic_fee
    #         FROM
    #           ordersEmMrg
    #         WHERE
    #           order_type='sell' AND buy_order_id IS NULL
    # """
    cnf.orders_infoEmMrg = {}
    for row in cursor.execute(orders_em_mrg,('sell',pair)):
        cnf.orders_infoEmMrg[str(row[0])] = dict(row)
        #return cnf.orders_infoEm

    # for row in cursor.execute(orders_em_mrg):
    #     cnf.orders_infoEmMrg[str(row[0])] = {'sell_order_id': row[0], 'order_type': row[1], 'order_pair': row[2], 'buy_order_id': row[3], 'sell_amount': row[4], 'sell_price': row[5], 'balance': row[6], 'balance_emta': row[7], 'profit': row[8],'panic_fee':row[9]}
    return cnf.orders_infoEmMrg

def add_new_order_SELL_emMRG(cursor, conn, pair_name, orderID, my_amount, my_need_price, spend_sum, prf,pf,os):
    cursor.execute(
        """
          INSERT INTO ordersEmMrg(
              order_type,
              order_pair,
              order_side,
              sell_order_id,
              sell_amount,
              sell_price,
              sell_created,
              sell_finished,
              balance,
              profit,
              panic_fee

          ) Values (
            'sell',
            :order_pair,
            :order_side,
            :sell_order_id,
            :sell_amount,
            :sell_price,
            :sell_created,
            :sell_finished,
            :balance,
            :profit,
            :panic_fee
          )
        """, {
            'order_pair': pair_name,
            'order_side': os,
            'sell_order_id': orderID,
            'sell_amount': my_amount,
            'sell_price': my_need_price,
            'sell_created': datetime.fromtimestamp(int(time.time())),
            'sell_finished':datetime.fromtimestamp(int(time.time())),
            'balance': spend_sum,
            'profit': prf,
            'panic_fee': pf
        }
    )

    conn.commit()

def update_buy_order_emMRG(cursor, conn, buy_order_id, sell_order_id, amount, price, income,sl):
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! update_buy_order_emMRG !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    force_buy_ = price if sl == 0 else 0 #if Stop loss
    price_ = price if sl == 1 else 0 #if not Stop loss
    cursor.execute(
        """
          UPDATE ordersEmMrg
          SET
            order_type = 'buy',
            buy_created = :dt1,
            buy_order_id = :buy_order_id,              
            buy_amount = :buy_amount,
            income = :income,
            buy_price = :buy_price,
            force_buy = :force_buy
          WHERE
            sell_order_id = :sell_order_id

        """, {
            'dt1': datetime.fromtimestamp(int(time.time())),
            'buy_order_id': buy_order_id,
            'buy_amount': amount,
            'income': income,
            'sell_order_id': sell_order_id,
            'buy_price': price_,
            'force_buy': force_buy_
        }
    )
    conn.commit()


def make_initial_table_emMRG_ShTr(cursor):
    # Если не существует таблиц, их нужно создать (первый запуск)
    orders_em_mrg = """
                  create table if not exists
                    ordersEmMrgShTr (
                      order_type TEXT,
                      order_pair TEXT,
                      order_side TEXT,
                      sell_order_id NUMERIC NULL,
                      sell_amount REAL NULL,
                      sell_price REAL NULL,
                      sell_created DATETIME NULL,
                      sell_finished DATETIME NULL,
                      buy_order_id NUMERIC,
                      buy_amount REAL,
                      buy_price REAL,
                      buy_created DATETIME,
                      force_buy INT DEFAULT 0,

                      panic_fee REAL NULL, 
                      income REAL NULL,                     
                      balance REAL NULL,
                      balance_emta REAL NULL,
                      profit REAL DEFAULT 0                                        
                    );
                """
    cursor.execute(orders_em_mrg)

def get_open_orders_emMRG_ShTr(cursor):
    orders_em_mrg = """
            SELECT    
             sell_order_id
            ,sell_created
            ,order_type
            ,order_pair
            ,buy_order_id
            ,sell_amount
            ,sell_price
            ,balance
            ,profit
            ,panic_fee
            FROM
              ordersEmMrgShTr
            WHERE
              order_type='sell' AND sell_finished NOT NULL
    """
    cnf.orders_infoEmMrgShTr = {}
    for row in cursor.execute(orders_em_mrg):
        cnf.orders_infoEmMrgShTr[str(row[0])] = dict(row)
    return cnf.orders_infoEmMrgShTr

def add_new_order_SELL_emMRG_ShTr(cursor, conn, pair_name, orderID, my_amount, my_need_price, spend_sum, prf,pf,os):
    cursor.execute(
        """
          INSERT INTO ordersEmMrgShTr(
              order_type,
              order_pair,
              order_side,
              sell_order_id,
              sell_amount,
              sell_price,
              sell_created,
              sell_finished,
              balance,
              profit,
              panic_fee

          ) Values (
            'sell',
            :order_pair,
            :order_side,
            :sell_order_id,
            :sell_amount,
            :sell_price,
            :sell_created,
            :sell_finished,
            :balance,
            :profit,
            :panic_fee
          )
        """, {
            'order_pair': pair_name,
            'order_side': os,
            'sell_order_id': orderID,
            'sell_amount': my_amount,
            'sell_price': my_need_price,
            'sell_created': datetime.fromtimestamp(int(time.time())),
            'sell_finished': datetime.fromtimestamp(int(time.time())),
            'balance': spend_sum,
            'profit': prf,
            'panic_fee': pf
        }
    )

    conn.commit()

def update_buy_order_emMRG_ShTr(cursor, conn, buy_order_id, sell_order_id, amount, price, income,sl):
    force_buy_ = price if sl == 0 else 0 #if Stop loss
    price_ = price if sl == 1 else 0 #if not Stop loss
    cursor.execute(
        """
          UPDATE ordersEmMrgShTr
          SET
            order_type = 'buy',
            buy_created = :dt1,
            buy_order_id = :buy_order_id,              
            buy_amount = :buy_amount,
            income = :income,
            buy_price = :buy_price,
            force_buy = :force_buy
          WHERE
            sell_order_id = :sell_order_id

        """, {
            'dt1': datetime.fromtimestamp(int(time.time())),
            'buy_order_id': buy_order_id,
            'buy_amount': amount,
            'income': income,
            'sell_order_id': sell_order_id,
            'buy_price': price_,
            'force_buy': force_buy_
        }
    )
    conn.commit()


def make_initial_tables_emTA(cursor):
    # Если не существует таблиц, их нужно создать (первый запуск)
    orders_em_ta = """
                  create table if not exists
                    ordersEmTa (
                      order_type TEXT,
                      order_pair TEXT,

                      buy_order_id NUMERIC,
                      buy_amount REAL,
                      buy_price REAL,
                      buy_created DATETIME,

                      sell_order_id NUMERIC NULL,
                      sell_amount REAL NULL,
                      sell_price REAL NULL,
                      sell_created DATETIME NULL,
                      force_sell INT DEFAULT 0,

                      panic_fee REAL NULL, 
                      income REAL NULL,                     
                      balance REAL NULL,
                      profit REAL NULL
                    );
                """
    cursor.execute(orders_em_ta)

def get_db_open_orders_emTA(cursor,pair):
    orders_em_ta = """
             SELECT buy_order_id ,order_type ,order_pair ,sell_order_id ,buy_amount ,buy_price,balance,profit,panic_fee,sell_price,buy_created
             FROM ordersEmTa WHERE order_type=? AND sell_order_id IS NULL AND order_pair=?
         """
        #.format(pr=pair)
    # orders_em_ta = """
    #         SELECT
    #          buy_order_id
    #         ,order_type
    #         ,order_pair
    #         ,sell_order_id
    #         ,buy_amount
    #         ,buy_price
    #         ,balance
    #         ,profit
    #         ,panic_fee
    #         ,sell_price
    #         ,buy_created
    #         FROM
    #           ordersEmTa
    #         WHERE
    #           order_type='buy' AND sell_order_id IS NULL AND order_pair = :pair
    # """
    cnf.orders_infoEm = {}
    #rows = cursor.execute(orders_em_ta)
    #if rows:
    for row in cursor.execute(orders_em_ta,('buy',pair)):
        cnf.orders_infoEm[str(row[0])] = dict(row)
    print('cnf.orders_infoEm ', cnf.orders_infoEm)
    return cnf.orders_infoEm

def add_new_order_buy_emTA(cursor, conn, pair_name, orderID, my_amount, buy_price, spend_sum, prf,selLMT,stloss):
    cursor.execute(
        """
          INSERT INTO ordersEmTa(
              order_type,
              order_pair,
              buy_order_id,
              buy_amount,
              buy_price,
              buy_created,
              balance,
              profit,
              sell_price,
              panic_fee

          ) Values (
            'buy',
            :order_pair,
            :order_id,
            :buy_order_amount,
            :buy_initial_price,
            :datetime_,
            :balance,
            :profit,
            :sell_price,
            :panic_fee
          )
        """, {
            'order_pair': pair_name,
            'order_id': orderID,
            'buy_order_amount': my_amount,
            'buy_initial_price': buy_price,
            'datetime_': datetime.fromtimestamp(int(time.time())),
            'balance': spend_sum,
            'profit': prf,
            'sell_price': selLMT,
            'panic_fee':stloss
        }
    )

    conn.commit()

def update_sell_emTA(cursor,conn, SorderID, ForderID, sell_amount, sell_price,fsell_price, balance, order, income,prf):
    orderID = SorderID if ForderID == 0 else ForderID
    cursor.execute(
        """
          UPDATE ordersEmTa
          SET
            order_type = 'sell',
            sell_order_id = :sell_order_id,
            sell_created = :datetime_,
            sell_amount = :sell_amount,
            sell_price = :cut_price,
            force_sell = :fcell,
            panic_fee = :panic_f,
            income = :income,
            balance = :balance,
            profit = :profit

          WHERE
            buy_order_id = :bOrderID
        """, {
            'sell_order_id': orderID,
            'sell_amount': sell_amount,
            'datetime_': datetime.fromtimestamp(int(time.time())),
            'cut_price': sell_price,
            'fcell': fsell_price,
            'panic_f': cnf.pairsGL[cnf.symbolPairGL]['stop_loss'],
            'income': income,
            'balance': balance,
            'bOrderID': order,
            'profit': prf
        }
    )
    conn.commit()



#table for Short Trade emulation
def make_initial_emTA_ShTr(cursor):
    # Если не существует таблиц, их нужно создать (первый запуск)22
    orders_em_ta_shtr = """
                  create table if not exists
                    ordersEmTaShTr (
                      order_type TEXT,
                      order_pair TEXT,

                      buy_order_id NUMERIC,
                      buy_amount REAL,
                      buy_price REAL,
                      buy_created DATETIME,

                      sell_order_id NUMERIC NULL,
                      sell_amount REAL NULL,
                      sell_price REAL NULL,
                      sell_created DATETIME NULL,
                      force_sell INT DEFAULT 0,

                      panic_fee REAL NULL, 
                      income REAL NULL,                     
                      balance REAL NULL,
                      profit REAL NULL
                    );
                """
    cursor.execute(orders_em_ta_shtr)
#fill dictionaryy
def get_open_orders_emTA_ShTr(cursor):
    orders_em_ta_shtr = """
            SELECT 
             buy_order_id
            ,order_type
            ,order_pair
            ,sell_order_id
            ,buy_amount
            ,buy_price
            ,balance
            ,profit
            ,panic_fee
            ,sell_price
            ,buy_created
            FROM
              ordersEmTaShTr
            WHERE
              order_type='buy' AND sell_order_id IS NULL
    """
    cnf.orders_infoEmShTr = {}
    for row in cursor.execute(orders_em_ta_shtr):
        cnf.orders_infoEmShTr[str(row[0])] = dict(row)
        return cnf.orders_infoEmShTr
#fill after buy
def add_new_order_buy_emTA_ShTr(cursor, conn, pair_name, orderID, my_amount, my_need_price, spend_sum, prf,pf,selLMT):
    cursor.execute(
        """
          INSERT INTO ordersEmTaShTr(
              order_type,
              order_pair,
              buy_order_id,
              buy_amount,
              buy_price,
              buy_created,
              balance,
              profit,
              panic_fee,
              sell_price

          ) Values (
            'buy',
            :order_pair,
            :order_id,
            :buy_order_amount,
            :buy_initial_price,
            :datetime_,
            :balance,
            :profit,
            :panic_fee,
            :sell_price
          )
        """, {
            'order_pair': pair_name,
            'order_id': orderID,
            'buy_order_amount': my_amount,
            'buy_initial_price': my_need_price,
            'datetime_': datetime.fromtimestamp(int(time.time())),
            'balance': spend_sum,
            'profit': prf,
            'panic_fee': pf,
            'sell_price': selLMT
        }
    )

    conn.commit()
#fill after sell
def update_sell_emTA_ShTr(cursor,conn, SorderID, ForderID, sell_amount, sell_price,fsell_price, balance, order, income, prf ):
    orderID = SorderID if ForderID == 0 else ForderID
    cursor.execute(
        """
          UPDATE ordersEmTaShTr
          SET
            order_type = 'sell',
            sell_order_id = :sell_order_id,
            sell_created = :datetime_,
            sell_amount = :sell_amount,
            sell_price = :cut_price,
            force_sell = :fcell,
            panic_fee = :panic_f,
            income = :income,
            balance = :balance,
            profit = :profit

          WHERE
            buy_order_id = :bOrderID
        """, {
            'sell_order_id': orderID,
            'sell_amount': sell_amount,
            'datetime_': datetime.fromtimestamp(int(time.time())),
            'cut_price': sell_price,
            'fcell': fsell_price,
            'panic_f': cnf.pairsGL[cnf.symbolPairGL]['stop_loss'],
            'income': income,
            'balance': balance,
            'bOrderID': order,
            'profit': prf
        }
    )
    conn.commit()
