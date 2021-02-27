import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as msg
from tkinter import scrolledtext
#from tkinter import Menu
from tkinter import Spinbox
#from tkinter import Radiobutton
import threading
#import keys
import AppEmulate
import AppWork
import AppEmMargin
import AppMargin
import configGlb as cnf
import HSTREmulate
#from binance.client import Client


# ===================================================================
class OOP:
    gbalance = {balance['asset']: float(balance['free']) for balance in cnf.bot.account()['balances'] if balance['asset'] == 'USDT'}
    mbalanceUSDT = {info['asset']: float(info['free']) for info in cnf.bot.marginAccount()['userAssets'] if info['asset'] == 'USDT'}
    mbalancesBTC = {info['asset']: float(info['free']) for info in cnf.bot.marginAccount()['userAssets'] if info['asset'] == 'BTC'}
    #mbalancesTRX = {info['asset']: float(info['free']) for info in cnf.bot.marginAccount()['userAssets'] if info['asset'] == 'TRX'}
    curr_rate = round(float(cnf.bot.tickerPrice(symbol='BTCUSDT')['price']),2)

    def __init__(self):  # Initializer method!
#         client = Client(keys.apikey, keys.apisecret)
# #        #AppWorkLMT.updatePortfolio()
#         self.assetsArray = client.get_account()
        # Create instance
        self.win = tk.Tk()

        self.win.title("Python bot for binance")

        self.tabControl = ttk.Notebook(self.win)  # Create Tab Control
        self.tab0 = ttk.Frame(self.tabControl)  # Create a tab
        self.tabControl.add(self.tab0, text='Settings')  # Add the tab

        self.tab1 = ttk.Frame(self.tabControl)  # Create a tab
        self.tabControl.add(self.tab1, text='Market analysis')  # Add the tab

        self.tab4 = ttk.Frame(self.tabControl)  # Create a tab
        self.tabControl.add(self.tab4, text='Trading Emulation')  # Add the tab

        self.tab2 = ttk.Frame(self.tabControl)  # Add a second tab
        self.tabControl.add(self.tab2, text='Trading Working  ')  # Make second tab visible

        self.tab3 = ttk.Frame(self.tabControl)  # Create a tab
        self.tabControl.add(self.tab3, text='Portfolio')  # Add the tab

        self.tabControl.pack(expand=True, fill="both")  # Pack to make visible

        #t1Frame1St = ttk.Style()
        #t1Frame1St.configure('Red.TLabelframe.Label', background='blue')

        self.t1Frame1 = tk.LabelFrame(self.tab0, bg="white", text=' ------------ General settings ---------------------------------  ')# style = "Font.TLabelframe")
        self.t1Frame1.grid(column=0, row=0, padx=4, pady=4, sticky='N')
        self.t1Frame11 = tk.LabelFrame(self.tab0, bg="white", text=' ----------- Short Trend and MACD Algorithms ---------------------------  ')
        self.t1Frame11.grid(column=1, row=0, padx=4, pady=4, sticky='N')
        # self.t1Frame12 = tk.LabelFrame(self.tab0, bg="white", text=' ----------- MACD Algorithms --------------------  ')
        # self.t1Frame12.grid(column=1, row=0, padx=4, pady=4, sticky='N')

        self.t1Frame4 = tk.LabelFrame(self.tab0, bg="white")
        self.t1Frame4.grid(column=1, row=0, padx=4, pady=4, sticky='S')
        self.t1Frame2 = tk.LabelFrame(self.tab1, bg="light blue")#, text=' -------- Trend and Volumes ------ ')
        self.t1Frame2.grid(column=0, row=1, padx=8, pady=4)
        self.t1Frame3 = tk.LabelFrame(self.tab1, bg="white", text=' -------- Algorithms  ------ ')
        self.t1Frame3.grid(column=0, row=0, padx=1, pady=4, sticky='EW')

        self.panel1 = ttk.LabelFrame(self.tab2, text=' Set parameters for trading ')
        self.panel1.grid(column=0, row=0, padx=8, pady=4)
        self.panel2 = ttk.LabelFrame(self.tab2, text=' ----- TRADING ----- ')
        self.panel2.grid(column=0, row=1, padx=8, pady=4)
        self.panel3 = ttk.LabelFrame(self.tab2, text=' bottom frame ')
        self.panel3.grid(column=0, row=2, padx=8, pady=4, sticky='W')

        self.panel31 = ttk.LabelFrame(self.tab3, text=' -------- Assets ------ ')
        self.panel31.grid(column=0, row=0, padx=8, pady=4)

        self.panel41 = ttk.LabelFrame(self.tab4, text=' -------- EMULATING  ------ ')
        self.panel41.grid(column=0, row=0, padx=8, pady=4)
        # LabelFrame using tab2 as the parent
# //////////////////// tab #0 Panel ////////////////////////////////////////////////////
        label_00 = ttk.Label(self.t1Frame1, text="Base:")
        label_00.grid(column=0, row=0, sticky='E')
        self.cmb_10 = ttk.Combobox(self.t1Frame1, values=cnf.pairs_2, width=6)
        self.cmb_10.current(0)
        self.cmb_10.grid(column=1, row=0)
        label00 = ttk.Label(self.t1Frame1, text="Quote:")
        label00.grid(column=0, row=1, sticky='E')
        self.cmb10 = ttk.Combobox(self.t1Frame1, values=cnf.pairs_, width=6)
        self.cmb10.current(0)
        self.cmb10.grid(column=1,row=1)

        label01 = ttk.Label(self.t1Frame1, text="Balance Spot and Fiat:")
        label01.grid(column=0, row=2, sticky='E')
        self.entry11_mess = tk.StringVar()
        self.entry11 = tk.Entry(self.t1Frame1, textvariable=self.entry11_mess, width=12)
        self.entry_m1 = self.gbalance['USDT']
        self.entry11_mess.set(self.entry_m1)
        self.entry11.grid(column=1, row=2)

        lblMrgBlnc = ttk.Label(self.t1Frame1, text="Balance Margin (Sell in USDT):")
        lblMrgBlnc.grid(column=0, row=3, sticky='E')
        self.entry12_mess = tk.StringVar()
        self.entry12 = tk.Entry(self.t1Frame1, textvariable=self.entry12_mess, width=12)
        self.entry_m2 = self.mbalanceUSDT['USDT']
        self.entry12_mess.set(self.entry_m2)
        self.entry12.grid(column=1,row=3)

        lblMrgBlnc2 = ttk.Label(self.t1Frame1, text="Balance Margin BTC :")
        lblMrgBlnc2.grid(column=0, row=4, sticky='E')
        self.entry13_mess = tk.StringVar()
        self.entry13 = tk.Entry(self.t1Frame1, textvariable=self.entry13_mess, width=12)
        self.entry13_mess.set(self.mbalancesBTC['BTC'])
        self.entry13.grid(row=4, column=1)
        self.entry14_mess = tk.StringVar()
        self.entry14 = tk.Entry(self.t1Frame1, textvariable=self.entry14_mess, width=12)
        self.entry14_mess.set(str(round(self.curr_rate * self.mbalancesBTC['BTC'],3)) + ' in USDT')
        self.entry14.grid(column=1,row=5)

        # self.entry15_mess = tk.StringVar()
        # self.entry15 = tk.Entry(self.t1Frame1, textvariable=self.entry15_mess, width=12)
        # self.entry15_mess.set(str(round(self.curr_rate * self.mbalancesTRX['TRX'],3)) + ' in TRX')
        # self.entry15.grid(column=1,row=19)

        labelSep1 = ttk.Label(self.t1Frame1, text="+++++++++++++++++++++++++++++++++")
        labelSep1.grid(column=0, row=6)
        label20 = ttk.Label(self.t1Frame1, text="Set delay to server (in secands):")
        label20.grid(column=0, row=7, sticky='E')
        self.cmb20 = ttk.Combobox(self.t1Frame1, values=cnf.mDelay, width=4)
        self.cmb20.current(1)
        self.cmb20.grid(column=1,row=7)

        labelCnTPos = ttk.Label(self.t1Frame1, text="Count positive trades:")
        labelCnTPos.grid(column=0, row=8, sticky='E')
        self.cmbCTPos = ttk.Combobox(self.t1Frame1, values=cnf.HSTR_countTrade, width=4)
        self.cmbCTPos.current(4)
        self.cmbCTPos.grid(column=1, row=8)
        labelTimeSel = ttk.Label(self.t1Frame1, text="Time for period:")
        labelTimeSel.grid(column=0, row=9, sticky='E')
        self.cmbTmFrame = ttk.Combobox(self.t1Frame1, values=cnf.HSTR_timeFrame, width=4)
        self.cmbTmFrame.current(0)
        self.cmbTmFrame.grid(column=1, row=9)

        labelSep01 = ttk.Label(self.t1Frame1, text="+++++++++++++++++++++++++++++ Long")
        labelSep01.grid(column=0, row=10)
        labelSep11 = ttk.Label(self.t1Frame1, text="++ Margin ++")
        labelSep11.grid(column=1, row=10)

        label02 = ttk.Label(self.t1Frame1, text="Loops:")
        label02.grid(column=0, row=11)
        self.spinLoop = Spinbox(self.t1Frame1, values=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15), width=4)# bd=9, command=self._spin)  # using range
        self.spinLoop.grid(column=0, row=11, sticky='E')
        self.spinLoopMrg = Spinbox(self.t1Frame1, values=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15), width=4)
        self.spinLoopMrg.grid(column=1, row=11)

        label03 = ttk.Label(self.t1Frame1, text="Profits:")
        label03.grid(column=0, row=12)
        self.cmb13 = ttk.Combobox(self.t1Frame1, values=cnf.mprofit, width=4)
        self.cmb13.current(2)
        self.cmb13.grid(column=0,row=12, sticky='E')
        self.cmbMrg = ttk.Combobox(self.t1Frame1, values=cnf.mprofit, width=4)
        self.cmbMrg.current(2)
        self.cmbMrg.grid(column=1,row=12)

        label05 = ttk.Label(self.t1Frame1, text="     Stop loss:")
        label05.grid(column=0, row=13)
        self.cmb15 = ttk.Combobox(self.t1Frame1, values=cnf.mstoploss, width=4)
        self.cmb15.current(0)
        self.cmb15.grid(column=0, row=13, sticky='E')
        self.cmbSlMrg = ttk.Combobox(self.t1Frame1, values=cnf.mstoploss, width=4)
        self.cmbSlMrg.current(0)
        self.cmbSlMrg.grid(column=1, row=13)

        label06 = ttk.Label(self.t1Frame1, text="Time Frame:")
        label06.grid(column=0, row=14)
        self.cmb06 = ttk.Combobox(self.t1Frame1, values=cnf.mKline, width=4)
        self.cmb06.current(1)
        self.cmb06.grid(column=0, row=14, sticky='E')
        self.cmbTfMrg = ttk.Combobox(self.t1Frame1, values=cnf.mKline, width=4)
        self.cmbTfMrg.current(1)
        self.cmbTfMrg.grid(column=1, row=14)
#####################################################################################################3
        #label10 = ttk.Label(self.t1Frame1, text="Delta for Limits($)")
        #label10.grid(column=0, row=15)

        self.var = tk.IntVar()
        self.cb = tk.Checkbutton(self.t1Frame1, text=" - Auto? Delta for Limits($) ", variable=self.var, onvalue=1, command=self.print_value)
        self.cb.select()
        self.cb.grid(column=0, row=15)

        self.cmb19 = ttk.Combobox(self.t1Frame1, values=cnf.limitUSD, width=4)
        self.cmb19.current(4)
        self.cmb19.grid(column=0, row=15, sticky='E')
        self.cmbDMrg = ttk.Combobox(self.t1Frame1, values=cnf.limitUSD, width=4)
        self.cmbDMrg.current(4)
        self.cmbDMrg.grid(column=1, row=15)

        labelSep1 = ttk.Label(self.t1Frame1, text="+++++++++++++++++++++++++++++++++")
        labelSep1.grid(column=0, row=16)
        self.rbVarMode = tk.IntVar()
        self.radSetEmul = tk.Radiobutton(self.t1Frame1, text="Trade Emulation", variable=self.rbVarMode, value=0, width=14, command=self.radCallMode)
        self.radSetEmul.grid(column=0, row=17, sticky='W')
        self.radSetEmul.select()

        self.radSetReal = tk.Radiobutton(self.t1Frame1, text="Trade Real        ", variable=self.rbVarMode, value=1, width=14, command=self.radCallMode)
        self.radSetReal.grid(column=0, row=18, sticky='W')

        btn53 = ttk.Button(self.t1Frame4, text="First Create DB!", command=lambda: self.db_init())
        btn53.grid(column=0, row=19, pady=10)

        self.rbVarM_L = tk.IntVar()
        self.rbVarM_ST = tk.IntVar()

        labelSep2 = ttk.Label(self.t1Frame11, text=" ++++++++++++++ MACD +++++++++++++++++++")
        labelSep2.grid(column=0, row=0)
        self.radMACD = tk.Radiobutton(self.t1Frame11, text="MACD Cross", variable=self.rbVarM_ST, value=0, width=12, command=self.radCall2)
        self.radMACD.grid(column=0, row=1, sticky='W')

        self.radLMT = tk.Radiobutton(self.t1Frame11, text="LIMIT", variable=self.rbVarM_L, value=1, width=8, command=self.radCallMrkt_Lmt)
        self.radLMT.grid(column=1, row=1, sticky='W')
        self.radLMT.select()
        self.radMRKT = tk.Radiobutton(self.t1Frame11, text="Market", variable=self.rbVarM_L, value=0, width=8, command=self.radCallMrkt_Lmt)
        self.radMRKT.grid(column=1, row=2, sticky='W')

        labelSep22 = ttk.Label(self.t1Frame11, text="+++++++++Short Trend +++++++++++++++++++")
        labelSep22.grid(column=0, row=3)
        self.radShTr = tk.Radiobutton(self.t1Frame11, text="Short Trend", variable=self.rbVarM_ST, value=1, width=12, command=self.radCall2)
        self.radShTr.grid(column=0, row=4, sticky='W')
        self.radShTr.select()
        self.radLMT = tk.Radiobutton(self.t1Frame11, text=" LIMIT", variable=self.rbVarM_L, value=1, width=8, command=self.radCallMrkt_Lmt)
        self.radLMT.grid(column=1, row=4, sticky='W')
        self.radLMT.select()
        self.radMRKT = tk.Radiobutton(self.t1Frame11, text="Market", variable=self.rbVarM_L, value=0, width=8, command=self.radCallMrkt_Lmt)
        self.radMRKT.grid(column=1, row=5, sticky='W')

        labelSep223 = ttk.Label(self.t1Frame11, text="---------------------------------- For Long(big Dn) ")
        labelSep223.grid(column=0, row=6)
        labelSep224 = ttk.Label(self.t1Frame11, text="For Margin(big Up)")
        labelSep224.grid(column=1, row=6)
        label09 = ttk.Label(self.t1Frame11, text="Number of candles: ")
        label09.grid(column=0, row=7, sticky='W')
        self.cmb18 = ttk.Combobox(self.t1Frame11, values=cnf.candleCount, width=6)
        self.cmb18.current(1)
        self.cmb18.grid(column=0, row=7, sticky='E')
        self.cmb18Dn = ttk.Combobox(self.t1Frame11, values=cnf.candleCount, width=6)
        self.cmb18Dn.current(1)
        self.cmb18Dn.grid(column=1, row=7)

        # labelSP = ttk.Label(self.t1Frame11, text="Minus Percent:")
        # labelSP.grid(column=0, row=8, sticky='W')
        # self.cmbSP = ttk.Combobox(self.t1Frame11, values=cnf.listPrntBigCandle, width=6)
        # self.cmbSP.current(3)
        # self.cmbSP.grid(column=0, row=8, sticky='E')
        # self.cmbSPDn = ttk.Combobox(self.t1Frame11, values=cnf.listPrntBigCandle, width=6)
        # self.cmbSPDn.current(3)
        # self.cmbSPDn.grid(column=1, row=8, sticky='E')

        self.varCB2 = tk.IntVar()
        self.cb2 = tk.Checkbutton(self.t1Frame11, text=" - Auto? Last candle Big(in %): ", variable=self.varCB2, onvalue=1, command=self.print_value)
        self.cb2.select()
        self.cb2.grid(column=0, row=9, sticky='W')
        #labelLastBig = ttk.Label(self.t1Frame11, text="Last candle Big(in %): ")
        #labelLastBig.grid(column=0, row=9, sticky='W')
        self.cmbBigDn = ttk.Combobox(self.t1Frame11, values=cnf.listPrntBigUpDn, width=6)
        self.cmbBigDn.current(0)
        self.cmbBigDn.grid(column=0, row=9, sticky='E')
        self.cmbBigUp = ttk.Combobox(self.t1Frame11, values=cnf.listPrntBigUpDn, width=6)
        self.cmbBigUp.current(0)
        self.cmbBigUp.grid(column=1, row=9)

        self.varCB3 = tk.IntVar()
        self.cb3 = tk.Checkbutton(self.t1Frame11, text=" - Auto? Last N candles Big(in %): ", variable=self.varCB3, onvalue=1, command=self.print_value)
        self.cb3.select()
        self.cb3.grid(column=0, row=10, sticky='W')
        #label3LastBig = ttk.Label(self.t1Frame11, text="Last N candles Big(in %): ")
        #label3LastBig.grid(column=0, row=10, sticky='W')
        self.cmb3BigDn = ttk.Combobox(self.t1Frame11, values=cnf.listPrnt3LstBigUpDn, width=6)
        self.cmb3BigDn.current(1)
        self.cmb3BigDn.grid(column=0, row=10, sticky='E')
        self.cmb3BigUP = ttk.Combobox(self.t1Frame11, values=cnf.listPrnt3LstBigUpDn, width=6)
        self.cmb3BigUP.current(1)
        self.cmb3BigUP.grid(column=1, row=10)

        # labelMCD5 = ttk.Label(self.t1Frame12, text="Limit for period: ") # Period
        # labelMCD5.grid(column=0, row=7, sticky='E')
        # self.cmbMCD4 = ttk.Combobox(self.t1Frame12, values=cnf.mKlineLimit, width=4)
        # self.cmbMCD4.current(8)
        # self.cmbMCD4.grid(column=1, row=7)

        style = ttk.Style()
        style.configure('W.TButton', font=('calibri', 20, 'bold'), foreground='red', width=25, height=15)
        btn52 = ttk.Button(self.t1Frame4, style = 'W.TButton', text="INIT PAIRS!", command=lambda: self.click_init(cnf.pairs))
        btn52.grid(column=0, row=0)
# //////////////////// tab #1 Panel  ////////////////////////////////////////////////////
        self.vLblAnl1 = tk.StringVar()
        self.vLblAnl1.set('Source data for trading')
        lblAnalys1 = ttk.Label(self.t1Frame3, textvariable=self.vLblAnl1)
        lblAnalys1.grid(column=0, row=0,  sticky='N')
        self.vLblAnl2 = tk.StringVar()
        self.vLblAnl2.set('Source data for Margin trading')
        lblAnalys2 = ttk.Label(self.t1Frame3, textvariable=self.vLblAnl2)
        lblAnalys2.grid(column=0, row=1,  sticky='N')
        self.vGMD = tk.StringVar()
        self.vGMD.set("Get Market Data")
        lblAnalys01 = ttk.Label(self.t1Frame2, text="Main Data")
        lblAnalys01.grid(column=0, row=0, sticky='W')
        self.analys01 = scrolledtext.ScrolledText(self.t1Frame2, width=70, height=30, wrap=tk.WORD, bg="black", fg="white")#tab Market Analysis 1th scrool
        self.analys01.grid(column=0, row=1, sticky='N')
        lblAnalys02 = ttk.Label(self.t1Frame2, text="Short Trend (algorithm)")
        lblAnalys02.grid(column=1, row=0)
        self.analys02 = scrolledtext.ScrolledText(self.t1Frame2, width=50, height=30, wrap=tk.WORD, bg="black", fg="white")#tab Market Analysis 2th scrool
        self.analys02.grid(column=1, row=1, padx=8)
        lbltab1MACD = ttk.Label(self.t1Frame2, text="Cross MACD (algorithm)")
        lbltab1MACD.grid(column=2, row=0)
        self.analys03 = scrolledtext.ScrolledText(self.t1Frame2, width=50, height=30, wrap=tk.WORD, bg="black",fg="white")  # tab Market Analysis 3th scrool
        self.analys03.grid(column=2, row=1, padx=8)

        self.vHSTR = tk.StringVar()
        self.vHSTR.set("HSTR Start ->")
        btn07_p2 = ttk.Button(self.t1Frame2, textvariable=self.vHSTR, command=self._HSTREm_alg)# tab Market Analysis
        btn07_p2.grid(column=0, row=4, pady=8, sticky='W')
        self.pb01_analis = ttk.Progressbar(self.t1Frame2, orient='horizontal', length=300, mode='determinate')
        self.pb01_analis.grid(row=4, column=0, pady=8, sticky='E')
        btnGetInfo = ttk.Button(self.t1Frame2, text='Get Info     ', command=self.getInfo)# tab Market Analysis
        btnGetInfo.grid(column=0, row=5, pady=8, sticky='W')



#////////////////////tab #4 Panel # ////////////////////////////////////////////////////
        self.scrol01_t1_01 = scrolledtext.ScrolledText(self.panel41, width=50, height=30, wrap=tk.WORD)#tab Trading Emulation 1th scrool
        self.scrol01_t1_01.grid(column=0, row=1, sticky='N')
        self.scrol01_t1_11 = scrolledtext.ScrolledText(self.panel41, width=60, height=15, wrap=tk.WORD, bg="black", fg="white")#tab Trading Emulation 2th scrool
        self.scrol01_t1_11.grid(column=1, row=1, sticky='N')
        self.scrol01_t1_111 = scrolledtext.ScrolledText(self.panel41, width=60, height=15, wrap=tk.WORD, bg="gray", fg="white")#tab Trading Emulation 3th scrool
        self.scrol01_t1_111.grid(column=1, row=1, sticky='S')

        label02_m2 = ttk.Label(self.panel41, text="Delay request to server -->")#tab Trading Emulation
        label02_m2.grid(column=0, row=0, sticky='E')
        self.pb00 = ttk.Progressbar(self.panel41, orient='horizontal', length=330, mode='determinate')#tab Trading Emulation
        self.pb00.grid(row=0, column=1, pady=10)
        self.pb01 = ttk.Progressbar(self.panel41, orient='horizontal', length=330, mode='determinate')#tab Trading Emulation
        self.pb01.grid(row=0, column=2, pady=10)

        self.scrol01_t1_12 = scrolledtext.ScrolledText(self.panel41, width=60, height=15, wrap=tk.WORD, bg="black", fg="white")#tab Trading Emulation 4th scrool
        self.scrol01_t1_12.grid(column=2, row=1, sticky='N')
        self.scrol01_t1_13 = scrolledtext.ScrolledText(self.panel41, width=60, height=15, wrap=tk.WORD, bg="gray", fg="white")#tab Trading Emulation 5th scrool
        self.scrol01_t1_13.grid(column=2, row=1, sticky='S')

        self.vtaEm = tk.StringVar()
        self.vtaEm.set("START Emulate TA")
        btn53 = ttk.Button(self.panel41, textvariable =self.vtaEm, command=self.emulateTA)
        btn53.grid(column=1, row=2, sticky='W')


        self.vtaEmMrg = tk.StringVar()
        self.vtaEmMrg.set("START Emulate Mrg")
        btn411 = ttk.Button(self.panel41, textvariable=self.vtaEmMrg, command=self.emulateMrg)
        btn411.grid(column=2, row=2, sticky='W')

# Tab Control 2 ----------We are creating a container frame to hold all other widgets------------------------------------------------------------
        self.vLbl00p1 = tk.StringVar()
        self.vLbl00p1.set('Source data for trading')
        self.label00_p1 = ttk.Label(self.panel1, textvariable=self.vLbl00p1)
        self.label00_p1.grid(column=0, row=0,  sticky='N')
        self.vLbl00p2 = tk.StringVar()
        self.vLbl00p2.set('Source data for Margin trading')
        self.label00_p1 = ttk.Label(self.panel1, textvariable=self.vLbl00p2)
        self.label00_p1.grid(column=0, row=1,  sticky='N')

        self.scrolT2S1 = scrolledtext.ScrolledText(self.panel2, width=50, height=30, wrap=tk.WORD, bg="green", fg="white")#tab Trading Working 1th scrool
        self.scrolT2S1.grid(column=0, row=1, sticky='W')
        self.scrolT2S2 = scrolledtext.ScrolledText(self.panel2, width=60, height=15, wrap=tk.WORD, bg="green", fg="white")
        self.scrolT2S2.grid(column=1, row=1, sticky='N')
        self.scrolT2S3 = scrolledtext.ScrolledText(self.panel2, width=60, height=15, wrap=tk.WORD, bg="dark green", fg="white")#tab Trading Working 3th scrool
        self.scrolT2S3.grid(column=1, row=1, sticky='S')
        self.scrolT2S4 = scrolledtext.ScrolledText(self.panel2, width=60, height=15, wrap=tk.WORD, bg="green", fg="white")#tab Trading Working 4th scrool
        self.scrolT2S4.grid(column=2, row=1, sticky='N')
        self.scrolT2S5 = scrolledtext.ScrolledText(self.panel2, width=60, height=15, wrap=tk.WORD, bg="dark green", fg="white")#tab Trading Working 4th scrool
        self.scrolT2S5.grid(column=2, row=1, sticky='S')
        label01_p2 = ttk.Label(self.panel2, text="Delay request to srv:")
        label01_p2.grid(column=1, row=0, sticky='W')
        self.pbT2S1 = ttk.Progressbar(self.panel2, orient='horizontal', length=280, mode='determinate')#tab Trading Work
        self.pbT2S1.grid(row=0, column=1, pady=10, sticky='E')
        self.pbT2S2 = ttk.Progressbar(self.panel2, orient='horizontal', length=280, mode='determinate')#tab Trading Work
        self.pbT2S2.grid(row=0, column=2, pady=10)

        self.vtaTrade = tk.StringVar()
        self.vtaTrade.set("START taTrade")
        btn04_p2 = ttk.Button(self.panel2, textvariable=self.vtaTrade, command=self.tradeTA)
        btn04_p2.grid(column=1, row=2, pady=10, sticky='W')

        # self.vtaTrade = tk.StringVar()
        # self.vtaTrade.set("START taTrade")
        btnSts = ttk.Button(self.panel2, text='Statistics for Session', command=self.sts)
        btnSts.grid(column=0, row=2, pady=10, sticky='W')

        self.vtaMrgTrade = tk.StringVar()
        self.vtaMrgTrade.set("START Short")
        btn05_p2 = ttk.Button(self.panel2, textvariable=self.vtaMrgTrade, command=self.tradeMGR)
        btn05_p2.grid(column=2, row=2, pady=10, sticky='W')

# Tab Control 3 ----------------------------------------------------------------------
        label3_11 = ttk.Label(self.panel31, text="Balance:")
        label3_11.grid(column=0, row=0, sticky='W')
        self.vLbl3_p1 = tk.StringVar()

        label_03 = ttk.Label(self.panel31, text="Get statistics on trade -> Select period:")
        label_03.grid(column=1, row=0, sticky='W')
        self.cmb_03 = ttk.Combobox(self.panel31, values=cnf.cmdays, width=9)
        self.cmb_03.current(0)
        self.cmb_03.grid(row=0, column=1, padx=4, pady=4, sticky='E')

        self.scrol3_p31_1 = scrolledtext.ScrolledText(self.panel31, width=52, height=30, wrap=tk.WORD, bg="yellow")
        self.scrol3_p31_1.grid(column=0, row=1, sticky='W')
        self.scrol3_p31_2 = scrolledtext.ScrolledText(self.panel31, width=52, height=30, wrap=tk.WORD, bg="yellow")
        self.scrol3_p31_2.grid(column=1, row=1, sticky='W')

        btn01_31 = ttk.Button(self.panel31, text="Get balance", command=self.portfBalance)
        btn01_31.grid(column=0, row=2, pady=10, sticky='W')
        btn01_32 = ttk.Button(self.panel31, text="Select profit Real", command=self.portfProfit)
        btn01_32.grid(column=1, row=2, pady=10, sticky='W')
        btn01_33 = ttk.Button(self.panel31, text="Select profit Emulate", command=self.portfProfitEm)
        btn01_33.grid(column=1, row=2, pady=10, sticky='E')

# Tab Control 1 FUNCTION &
################################################################################################
    # def thread(fn):
    #     def execute(*args, **kwargs):
    #         threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    #     return execute
    def db_init(self):
        AppWork.firstInitDB()

    def click_init(self,_pairs):
        self.t1Frame1.update()
        _pairs = [
               {
                   'base': 'USDT',
                   'quote': self.cmb10.get(),
#                   'offers_amount': int(self.cmb14.get()),
                   'spend_sum':  round(float(self.entry11.get()),4),  # Сколько тратить base каждый раз при покупке quote
                   'spend_sum_mrg':  round(float(self.entry13.get()),6),
                   'profit_markup': float(self.cmb13.get()),  # Какой навар нужен с каждой сделки? (0.001 = 0.1%)
                   'profit_markupMrg': float(self.cmbMrg.get()),
                   'use_stop_loss': True,  # Нужно ли продавать с убытком при падении цены
                   'stop_loss': float(self.cmb15.get()),  # 2%  - На сколько должна упасть цена, что бы продавать с убытком
                   'stop_lossMrg': float(self.cmbSlMrg.get())
               }
             ]
        #print('_pairs[0][spend_sum_mrg] ',_pairs[0]['spend_sum_mrg'])
        cnf.loopGL = int(self.spinLoop.get())
        #print('cnf.loopGL: ',cnf.loopGL)
        cnf.loopMrgGL = int(self.spinLoopMrg.get())
        #print('cnf.loopMrgGL: ',cnf.loopMrgGL)
        #print('_pairs: ',_pairs)
        cnf.pairsGL = _pairs
        cnf.nLMT_GL = float(self.cmb19.get())#limit cost for Buy
        cnf.nLMT_GL_CheckB = self.var.get() # get value of CheckBox 1-select, 0-deselect
        cnf.nLMT_MrgGL = float(self.cmbDMrg.get()) #limit cost for Sell
        cnf.BigUpDn_CheckB = self.varCB2.get() # get value of CheckBox 1-select, 0-deselect
        cnf.KlineGL = self.cmb06.get() #time frame for long
        cnf.BUYlng_LIFE_TIME_MIN = int(str(cnf.KlineGL)[0]) #life time for buing (correct only until 5min)
        cnf.KlineMrgGL = self.cmbTfMrg.get() #time frame for Margin
        cnf.SELLshrt_LIFE_TIME_MIN = int(str(cnf.KlineMrgGL)[0]) #life time for selling (correct only until 5min)
        #print('cnf.KlineGL: ' + str(cnf.BUYlng_LIFE_TIME_MIN) +'; cnf.KlineMrgGL: ' + str(cnf.SELLshrt_LIFE_TIME_MIN))
        cnf.KLINES_LIMITS = 101 #self.cmb17.get() #count of klines
        cnf.fastMoveCount = self.cmb18.get()
        cnf.chVarDelay_GL = float(self.cmb20.get())/100
        cnf.symbolPairGL = _pairs[0]['quote'] + _pairs[0]['base']#!!!!!^%????????
        # формируем словарь из указанных пар, для удобного доступа
        cnf.pairsGL = {pair['quote'].upper() + pair['base'].upper(): pair for pair in cnf.pairsGL}
        cnf.pairsGL[cnf.symbolPairGL]['use_stop_loss'] = False if cnf.pairsGL[cnf.symbolPairGL]['stop_loss'] == 0 else True
        #cnf.first_balanceGL = self.entry11.get()
        for pair_name, pair_obj in cnf.pairsGL.items():
            cnf.pairsGL_out = 'Pair: ' + str(pair_name) + '; Spend sum: ' + str(pair_obj['spend_sum']) + '; Spend sum Margin: '+ str(pair_obj['spend_sum_mrg']) + '; Profit markup: ' + str(pair_obj['profit_markup']) \
                              + '; Stop loss: ' + str(pair_obj['stop_loss']) +'; Stop loss? - ' + str(pair_obj['use_stop_loss'])

            cnf.pairsGL_outMrg = 'Pair: ' + str(pair_name) + '; Spend sum: ' + str(pair_obj['spend_sum']) + '; Spend sum Margin: '+ str(pair_obj['spend_sum_mrg']) + '; Profit markup Margin: ' + str(pair_obj['profit_markupMrg']) \
                                 + '; Stop loss: ' + str(pair_obj['stop_loss']) + '; Stop loss? - ' + str(pair_obj['use_stop_loss'])


        self.vLbl00p1.set(cnf.pairsGL_out) #for display data on tab (set for Labels)
        self.vLbl00p2.set(cnf.pairsGL_outMrg)
        self.vLblAnl1.set(cnf.pairsGL_out)
        self.vLblAnl2.set(cnf.pairsGL_outMrg)

        cnf.countPos = int(self.cmbCTPos.get())
        cnf.timeFrame = str(self.cmbTmFrame.get())
        #cnf.setExtremPercent = float(self.cmbSP.get())
        #cnf.setExtremPercentDn = float(self.cmbSPDn.get())
        # cnf.bigUpPercent = float(self.cmbBigUp.get()) # for Margin
        # cnf.bigDnPercent = float(self.cmbBigDn.get()) # for Long
        # cnf.Up3LastSet = float(self.cmb3BigUP.get()) # for Margin
        # cnf.Dn3LastSet = float(self.cmb3BigDn.get()) # for Long


    def _quit(self):
        self.win.quit()
        self.win.destroy()
        exit()

    # def _HSTREm(self):
    #     HSTREmulate.HSTREm(self.analys01)

    def _HSTREm_alg(self):
        if cnf.HSTRLoop_GL == False:
            cnf.HSTRLoop_GL = True
            self.vHSTR.set('HSTR Start ->  Working!')
            HSTREmulate.HSTREm_algorithm(self.scrol01_t1_01,self.scrol01_t1_11,self.scrol01_t1_111,self.scrol01_t1_12,self.scrol01_t1_13, self.analys01, self.pb01_analis,self.pb00,self.pb01,self.analys02,
                                         self.scrolT2S1, self.scrolT2S2, self.scrolT2S3, self.pbT2S1, self.scrolT2S4,self.scrolT2S5, self.pbT2S2,self.analys03)
            cnf.loop_AppWrkShTr, cnf.loop_AppWrk, cnf.loop_AppMrgMACD,cnf.loop_AppMrgShTr = 0,0,0,0

        else:
            cnf.HSTRLoop_GL = False
            self.vHSTR.set('HSTR Start ->  Stopped!')


        # Tab Control 2 FUNCTION &
################################################################################################

    def tradeTA(self):
        if cnf.isMACD_GL:
            if cnf.App_freezLong_GL == False:
                cnf.loop_AppWrk = 0 # if not first press
                cnf.App_freezLong_GL = True
                self.vtaTrade.set("taTradeM - Working")
                AppWork.taTradeMACD(self.scrolT2S1, self.scrolT2S2, self.scrolT2S3, self.pbT2S1)
                print('1 ',str(cnf.App_freezLong_GL))
            else:
                cnf.App_freezLong_GL = False
                cnf.loop_AppWrk = cnf.loopGL
                self.vtaTrade.set("taTradeM - Stoped!")
                print('2 ',str(cnf.App_freezLong_GL))

        if cnf.isSTrend_GL:
            if cnf.App_freezLong_GL == False:
                cnf.loop_AppWrkShTr = 0 # if not first press
                cnf.App_freezLong_GL = True
                self.vtaTrade.set("taTradeST - Working")
                AppWork.taTradeShTrend(self.scrolT2S1, self.scrolT2S2, self.scrolT2S3, self.pbT2S1)
                print('3 ',str(cnf.App_freezLong_GL))
            else:
                cnf.App_freezLong_GL = False
                cnf.loop_AppWrkShTr = cnf.loopGL
                self.vtaTrade.set("taTradeST - Stoped!")
                print('4 ',str(cnf.App_freezLong_GL))

    def tradeMGR(self):
        if cnf.isMACD_GL:
            if cnf.AppMrg_freezShort_GL == False:
                cnf.loop_AppMrgMACD = 0 # if not first press
                cnf.AppMrg_freezShort_GL = True
                self.vtaMrgTrade.set("MACDShort - Working")
                AppMargin.mrgTradeMACD(self.scrolT2S1, self.scrolT2S4,self.scrolT2S5, self.pbT2S2)
                print('1 ',str(cnf.AppMrg_freezShort_GL))
            else:
                cnf.AppMrg_freezShort_GL = False
                cnf.loop_AppMrgMACD = cnf.loopGL
                self.vtaMrgTrade.set("MACDShort - Stopped!")
                print('2 ',str(cnf.AppMrg_freezShort_GL))
            
        if cnf.isSTrend_GL:
            if cnf.AppMrg_freezShort_GL == False:
                cnf.loop_AppMrgShTr = 0 # if not first press
                cnf.AppMrg_freezShort_GL = True
                self.vtaMrgTrade.set("ShTrShort - Working")
                AppMargin.mrgTradeShTr(self.scrolT2S1, self.scrolT2S4,self.scrolT2S5, self.pbT2S2)
                print('3 ',str(cnf.AppMrg_freezShort_GL))
            else:
                cnf.AppMrg_freezShort_GL = False
                cnf.loop_AppMrgShTr = cnf.loopGL
                self.vtaMrgTrade.set("ShTrShort - Stopped!")
                print('4 ',str(cnf.AppMrg_freezShort_GL))

    def emulateTA(self):
        if cnf.isMACD_GL:
            if cnf.eml_freezLong_GL == False:
                self.vtaEm.set("EmMACD - Working")
                cnf.loop_AppEmul = 0 # if not first press
                cnf.eml_freezLong_GL = True #if start by button
                AppEmulate.e_taTradeMACD(self.scrol01_t1_01, self.scrol01_t1_11, self.scrol01_t1_111, self.pb00)# scrools 1,2,3
                print('1 ',str(cnf.eml_freezLong_GL))
            else:
                cnf.eml_freezLong_GL = False
                cnf.loop_AppEmul = cnf.loopGL
                self.vtaEm.set("EmMACD - Stopped!")
                print('2 ',str(cnf.eml_freezLong_GL))

        if cnf.isSTrend_GL:
            if cnf.eml_freezLong_GL == False:
                self.vtaEm.set("EmTaShTr - Working")
                cnf.loop_AppEmulShTr = 0 # if not first press
                cnf.eml_freezLong_GL = True #if start by button
                AppEmulate.e_taTradeShTrend(self.scrol01_t1_01, self.scrol01_t1_11, self.scrol01_t1_111, self.pb00)# scrools 1,2,3
                print('3 ',str(cnf.eml_freezLong_GL))
            else:
                cnf.eml_freezLong_GL = False
                cnf.loop_AppEmulShTr = cnf.loopGL
                self.vtaEm.set("EmTaShTr - Stopped!")
                print('4 ',str(cnf.eml_freezLong_GL))

    def emulateMrg(self):
        if cnf.isMACD_GL:
            if cnf.eml_freezLong_GL == False:
                self.vtaEmMrg.set("EmMrgMACD - Working")
                cnf.loop_AppEmMrg = 0 # if not first press
                cnf.eml_freezLong_GL = True #if start by button
                AppEmMargin.emrg_taTradeMACD(self.scrol01_t1_01, self.scrol01_t1_12, self.scrol01_t1_13, self.pb01)# scrools 1,4,5
                print('1 ',str(cnf.eml_freezLong_GL))
            else:
                cnf.eml_freezLong_GL = False
                cnf.loop_AppEmMrg = cnf.loopMrgGL
                self.vtaEmMrg.set("EmMrgMACD - Stopped!")
                print('2 ',str(cnf.eml_freezLong_GL))

        if cnf.isSTrend_GL:
            if cnf.eml_freezLong_GL == False:
                self.vtaEmMrg.set("EmMrgShTr - Working")
                cnf.loop_AppEmMrgShTr = 0 # if not first press
                cnf.eml_freezLong_GL = True #if start by button
                AppEmMargin.emrg_taTradeShTr(self.scrol01_t1_01, self.scrol01_t1_12, self.scrol01_t1_13, self.pb01)# scrools 1,4,5
                print('3 ',str(cnf.eml_freezLong_GL))
            else:
                cnf.eml_freezLong_GL = False
                cnf.loop_AppEmMrgShTr = cnf.loopMrgGL
                self.vtaEmMrg.set("EmMrgShTr - Stopped!")
                print('4 ',str(cnf.eml_freezLong_GL))

    def getInfo(self):
        AppEmulate.getInfo(self.analys01,self.analys02,self.analys03)

# Tab Control 3 FUNCTION &
################################################################################################
    def portfBalance(self): # get balance
        AppWork.portfolio(self.scrol3_p31_1)

    def portfProfit(self):
        cnf.wdays = self.cmb_03.get()
        AppWork.portfolioProf(self.scrol3_p31_2, 1)

    def portfProfitEm(self):
        cnf.wdays = self.cmb_03.get()
        AppWork.portfolioProf(self.scrol3_p31_2, 0)
    #@thread

    def sts(self):
        AppMargin.StaticSession(self.scrolT2S1)

    def Callback(self):
        #HSTREmulate.startW(OOP().win)
        msg.showinfo("HSTREmulate", 'test double click!')


    # Radiobutton Callback
    def radCallMrkt_Lmt(self):
        radSel = self.rbVarM_L.get()
        if radSel == 0:
            cnf.isMRKT_GL = True
            cnf.isLMT_GL = False
        elif radSel == 1:
            cnf.isLMT_GL = True
            cnf.isMRKT_GL = False
            #print('if select Limit', cnf.isLMT_GL)

    def radCall2(self):
        radSel2 = self.rbVarM_ST.get()
        if radSel2 == 0:
            cnf.isMACD_GL = True
            cnf.isSTrend_GL = False
            print('if select MACD Cross', cnf.isMACD_GL)
        elif radSel2 == 1:
            cnf.isSTrend_GL = True
            cnf.isMACD_GL = False
            print('if select Short Trend', cnf.isSTrend_GL)
    def radCallMode(self):
        radSel = self.rbVarMode.get()
        if radSel == 0:
            cnf.driveMode = 0
            #print('if select Trade Emulation', cnf.driveMode )
        elif radSel == 1:
            cnf.driveMode = 1
            #print('if select Trade Real', cnf.driveMode )




    def print_value(self):
        print(cnf.nLMT_GL_CheckB)
#OOP().win.mainloop()