import config 

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

import mysql.connector as mysql

import time

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import QueryOrderStatus


def submit_order():

    # get market order request info
    client_id = e_client_id.get()
    symbol = e_ticker.get()
    qty = e_qty.get()
    side = OrderSide.BUY if side_combobox.get() == "BUY" else OrderSide.SELL
    time_in_force = TimeInForce.DAY

    if (not client_id) or (not symbol) or(not qty) or  (not side) or (not time_in_force):
        messagebox.showinfo(title="Order Status", message="All fields are required")
        
    else:
        if not market_open:
            messagebox.showinfo(title="Order Status", message= "Market is closed until next open time: "+ str(next_open)+ "Eastern Time" )


        else:
            # submit market order
            market_order_data = MarketOrderRequest(symbol =symbol.upper(), qty = float(qty),side= side,time_in_force = time_in_force)
            market_order = trading_client.submit_order(order_data = market_order_data)
            messagebox.showinfo(title ="Order Status", message = 'Success')



# save all_order from alpaca plateform including prices _to_database
def save_order_to_db():
    # Get the latest closed order 
    time.sleep(1)
    get_orders_data = GetOrdersRequest(status=QueryOrderStatus.CLOSED,limit=100,nested=True)
    temp =trading_client.get_orders(filter=get_orders_data)[0]
    order_id = str(temp.client_order_id)
    side= temp.side[:]
    symbol = temp.symbol
    qty = str(temp.qty)
    purchase_price = str(temp.filled_avg_price)
    client_id = e_client_id.get()

    #save to database
    con = mysql.connect(host="localhost", user="dbuser", password="dbuserdbuser", database="client_stock_order")
    cursor = con.cursor()
    cursor.execute("Insert into stock_order values('"+ order_id +"','"+ client_id +"','"+ symbol +"','"+ qty +"','"+ side +"','"+ purchase_price +"')")
    cursor.execute("commit")
    con.close()


def show_order_on_box():
    get_orders_data = GetOrdersRequest(status=QueryOrderStatus.CLOSED,limit=100,nested=True)
    temp =trading_client.get_orders(filter=get_orders_data)[0]
    order_id = str(temp.client_order_id)
    side= temp.side[:]
    symbol = temp.symbol
    qty = str(temp.qty)
    purchase_price = str(temp.filled_avg_price)
    order_list.insert(tk.END, side+ "   " + symbol +"   " + qty)




def combine_funcs(*funcs):
    def combined_func(*args, **kwargs):
        for f in funcs:
            f(*args, **kwargs)
    return combined_func



# get account info
trading_client = TradingClient(config.API_KEY, config.API_SECRET_KEY, paper=True)
account = trading_client.get_account()
market_open = trading_client.get_clock().is_open
next_open = trading_client.get_clock().next_open



root = tk.Tk()
root.geometry("500x300")
root.title("Order Tool")
order_list = tk.Listbox(root, height=15)

client_id = tk.Label(root, text="Client ID", font=('Arial', 10))
client_id.place(x=20, y =30)

ticker = tk.Label(root, text="Stock Symbol", font=('Arial', 10))
ticker.place(x=20, y =60)

qty = tk.Label(root, text="Quantity", font=('Arial', 10))
qty.place(x=20, y =90)

side = tk.Label(root, text="Order Side", font=('Arial', 10))
side.place(x=20, y =120)

e_client_id = tk.Entry()
e_client_id.place(x= 150, y =30)

e_ticker = tk.Entry()
e_ticker.place(x=150, y=60)

e_qty = tk.Entry()
e_qty.place(x=150, y=90)


side_combobox = ttk.Combobox(root, values=['BUY', 'SELL'])
side_combobox.place(x=150, y=120)


place_order = tk.Button(root, text="Submit", font=('Arial', 10), bg='white',command= combine_funcs(submit_order,save_order_to_db, show_order_on_box) )
place_order.place(x=150, y=150)


order_list.place(x=340, y =30)

root.mainloop()