from tkinter import *
from tkinter import ttk
import sqlite3
import time
import threading
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from kiteconnect import KiteConnect

root=Tk()
root.geometry("700x550")
root.config(background="black")
style= ttk.Style()
style.theme_use('winnative')
stopScan=False
def startThread():
    t1=threading.Thread(target=optionChain)
    t1.start()

def connectZerodha():
    global kite
    kite=KiteConnect(api_key="")
    request_token=entryToken.get()
    data=kite.generate_session(request_token,api_secret="")
    kite.set_access_token(data["access_token"])
    top.destroy()
    expiry()
    connectButton.config(bg="palegreen",text="CONNECTED")
def popup():
    global top,entryToken
    top=Toplevel(root)
    entryToken=ttk.Entry(top)
    entryToken.grid(row=0,column=0)	
    Button(top,text="SUBMIT",command=connectZerodha).grid(row=0,column=1)
    
def expiry():
    quote=(kite.quote("NSE:NIFTY BANK"))
    price=(quote["NSE:NIFTY BANK"]["last_price"])
    price=(int(price)-(int)(price)%100)
    i=0
    error=False
    expireArray=[]
    while(i<30):
        year=(datetime.today()+timedelta(days=i)).strftime("%y")
        month=(int)((datetime.today()+timedelta(days=i)).strftime("%m"))
        day=(datetime.today()+timedelta(days=i)).strftime("%d")
        strike="BANKNIFTY"+str(year)+str(month)+str(day)+str(price)+"CE"
        try:
            quote=(kite.quote("NFO:"+strike))
            last_price=(quote["NFO:"+strike]["last_price"])
            expireArray.append(str(year)+"-"+str(month)+"-"+str(day))
        except:
            error=True
        i+=1
    year=(datetime.today()).strftime("%y")    
    month=((datetime.today()).strftime("%b")).upper()
    strike="BANKNIFTY"+str(year)+str(month)+str(price)+"CE"
    try:
        quote=(kite.quote("NFO:"+strike))
        print(quote)
        last_price=(quote["NFO:"+strike]["last_price"])
    except:
        year=(datetime.today()+relativedelta(months=1)).strftime("%y")    
        month=((datetime.today()+relativedelta(months=1)).strftime("%b")).upper()
    expireArray.append(str(year)+"-"+str(month))
    expiries["values"]=expireArray
def optionChain():
    global chainFrame
    strikeCount=20
    incrementor=50
    try:
        chainFrame.destroy()
    except:
        print()
    chainFrame=Frame(root)
    canvas=Canvas(chainFrame)
    scrollbar=ttk.Scrollbar(chainFrame,orient="vertical",command=canvas.yview)
    scrollableFrame=ttk.Frame(canvas)
    scrollableFrame.bind("<Configure>",lambda e:canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0,0),window=scrollableFrame,anchor="nw")
    canvas.configure(width=700,yscrollcommand=scrollbar.set)
    canvas.configure(height=700)
    canvas.pack(side="left",fill="both",expand=True)
    scrollbar.pack(side="right",fill="y")
    chainFrame.pack()
    quote=(kite.quote("NSE:NIFTY 50"))
    price=(quote["NSE:NIFTY 50"]["last_price"])
    if(index.get()=="BANKNIFTY"):
        quote=(kite.quote("NSE:NIFTY BANK"))
        price=(quote["NSE:NIFTY BANK"]["last_price"])
        incrementor=100
    price=(int(price)-(int)(price)%incrementor)
    Label(scrollableFrame,text="CE_OI",width=10,bg="gray",font=("Arial Black",10)).grid(row=0,column=0)
    Label(scrollableFrame,text="LTP",width=10,bg="gray",font=("Arial Black",10)).grid(row=0,column=1)
    Label(scrollableFrame,text="CHANGE",width=10,bg="gray",font=("Arial Black",10)).grid(row=0,column=2)
    Label(scrollableFrame,text="STRIKE",width=10,bg="gray",font=("Arial Black",10)).grid(row=0,column=3)
    Label(scrollableFrame,text="LTP",width=10,bg="gray",font=("Arial Black",10)).grid(row=0,column=4)
    Label(scrollableFrame,text="CHANGE",width=10,bg="gray",font=("Arial Black",10)).grid(row=0,column=5)
    Label(scrollableFrame,text="PE_OI",width=10,bg="gray",font=("Arial Black",10)).grid(row=0,column=6)
    i=1
    price-=(int)((strikeCount/2)*incrementor)
    instruments=[]
    while(i<=strikeCount):
        strike=expiries.get()
        strike=strike.replace("-","")
        strike=index.get()+strike+str(price)
        instruments.append("NFO:"+strike+"CE")
        instruments.append("NFO:"+strike+"PE")
        Label(scrollableFrame,text="",width=10,font=("Arial bold",10)).grid(row=i,column=0)
        Label(scrollableFrame,text="",width=10,font=("Arial bold",10)).grid(row=i,column=1)
        Label(scrollableFrame,text="",width=10,font=("Arial bold",10)).grid(row=i,column=2)
        label=Label(scrollableFrame,text=price,width=10,bg="burlywood2",font=("Arial bold",10))
        label.grid(row=i,column=3)
        Label(scrollableFrame,text="",width=10,font=("Arial bold",10)).grid(row=i,column=4)
        Label(scrollableFrame,text="",width=10,font=("Arial bold",10)).grid(row=i,column=5)
        Label(scrollableFrame,text="",width=10,font=("Arial bold",10)).grid(row=i,column=6)
        if(i==strikeCount/2):
            label.config(bg="springgreen")
        i+=1
        price+=incrementor
    quote=(kite.quote(instruments))
    i=1
    
    while(i<=strikeCount):
        widgets=scrollableFrame.winfo_children()
        widgets[i*7+1]["text"]=quote[instruments[(i-1)*2]]["last_price"]
        oi_data(quote[instruments[((i-1)*2)]]["instrument_token"],widgets[i*7],widgets[i*7+2],widgets[i*7+1])
        
        widgets[i*7+4]["text"]=quote[instruments[((i-1)*2)+1]]["last_price"]
        oi_data(quote[instruments[((i-1)*2)+1]]["instrument_token"],widgets[i*7+6],widgets[i*7+5],widgets[i*7+4])
        i+=1 
def oi_data(token,widget1,widget2,widget3):

        to_date=datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        from_date = ((datetime.today()-timedelta(days=7)).strftime("%Y-%m-%d"))+" 09:15:00"
        data=(kite.historical_data(token, from_date, to_date, timeFrame.get(),False,True))
        widget1["text"]=data[len(data)-1]["oi"]
        widget2["text"]=data[len(data)-1]["oi"]-data[len(data)-2]["oi"]
        if(data[len(data)-1]["oi"]-data[len(data)-2]["oi"]>500000):
            widget1.config(bg="palegreen")
            widget2.config(bg="palegreen")
            widget3.config(bg="palegreen")
        elif(data[len(data)-1]["oi"]-data[len(data)-2]["oi"]<0):
            widget1.config(bg="red")
            widget2.config(bg="red")
            widget3.config(bg="red")
        else:
            widget1.config(bg="tomato1")
            widget2.config(bg="tomato1")
            widget3.config(bg="tomato1")
          
topFrame=Frame(root)
connectButton=Button(topFrame,text="NOT CONNECTED",command=popup,width=13,bg="red",fg="black",font=("Arial Black",10))
connectButton.grid(row=0,column=0)
index=ttk.Combobox(topFrame,values=["NIFTY","BANKNIFTY"],width=13,font=("Arial Bold",10))
index.grid(row=0,column=1)
expiries=ttk.Combobox(topFrame,values=[],width=13,font=("Arial Bold",10))
expiries.grid(row=0,column=2)
timeFrame=ttk.Combobox(topFrame,values=["5minute","10minute","15minute","30minute","60minute","day"],width=13,font=("Arial Bold",10))
timeFrame.grid(row=0,column=3)
Button(topFrame,text="OPTION CHAIN",command=startThread,width=13,bg="palegreen",fg="black",font=("Arial Black",10)).grid(row=0,column=4)
topFrame.config(background="black")
topFrame.pack()

root.mainloop()


# IMPLEMENT THREAD TO SPEED UP

while(i<=strikeCount):
        widgets=scrollableFrame.winfo_children()
        widgets[i*7+1]["text"]=quote[instruments[(i-1)*2]]["last_price"]
        t1=threading.Thread(target=oi_data,args=(quote[instruments[(i-1)*2]]["instrument_token"],widgets[i*7],widgets[i*7+2],widgets[i*7+1]))
        t1.start()
        widgets[i*7+4]["text"]=quote[instruments[((i-1)*2)+1]]["last_price"]
        t1=threading.Thread(target=oi_data,args=(quote[instruments[((i-1)*2)+1]]["instrument_token"],widgets[i*7+6],widgets[i*7+5],widgets[i*7+4]))
        t1.start()
        i+=1

