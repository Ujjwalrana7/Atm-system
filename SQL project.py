import tkinter as tk
from tkinter import messagebox
import mysql.connector
import random

# ---------- DATABASE CONNECTION ----------
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",         # change if needed
        password="07Dec@",  # replace with your MySQL password
        database="atm_system"
    )
# ---------- ATM MAIN WINDOW ----------
class ATMApp:
    def __init__(self, master, account_no):
        self.master = master
        self.account_no = account_no
        self.master.title("ATM Machine System")
        self.master.geometry("400x400")
        
        self.label = tk.Label(master, text="ATM Operations", font=("Arial", 16, "bold"))
        self.label.pack(pady=10)
        
        tk.Button(master, text="Deposit", command=self.deposit).pack(pady=5)
        tk.Button(master, text="Withdraw", command=self.withdraw).pack(pady=5)
        tk.Button(master, text="Check Balance", command=self.check_balance).pack(pady=5)
        tk.Button(master, text="View Transactions", command=self.view_transactions).pack(pady=5)
        tk.Button(master, text="Exit", command=master.quit).pack(pady=10)
    
    def deposit(self):
        amount = random.randint(1000, 10000)
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO transactions (account_no, transaction_type, amount) VALUES (%s, 'Deposit', %s)", (self.account_no, amount))
        cur.execute("UPDATE accounts SET balance = balance + %s WHERE account_no = %s", (amount, self.account_no))
        conn.commit()
        conn.close()
        messagebox.showinfo("Deposit Successful", f"₹{amount} deposited successfully!")

    def withdraw(self):
        amount = random.randint(500, 8000)
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT balance FROM accounts WHERE account_no = %s", (self.account_no,))
        balance = cur.fetchone()[0]
        if amount > balance:
            messagebox.showwarning("Insufficient Funds", "Not enough balance to withdraw.")
        else:
            cur.execute("INSERT INTO transactions (account_no, transaction_type, amount) VALUES (%s, 'Withdraw', %s)", (self.account_no, amount))
            cur.execute("UPDATE accounts SET balance = balance - %s WHERE account_no = %s", (amount, self.account_no))
            conn.commit()
            messagebox.showinfo("Withdrawal Successful", f"₹{amount} withdrawn successfully!")
        conn.close()
    
    def check_balance(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT holder_name, bank_name, balance FROM accounts WHERE account_no = %s", (self.account_no,))
        result = cur.fetchone()
        conn.close()
        messagebox.showinfo("Account Balance", f"Name: {result[0]}\nBank: {result[1]}\nBalance: ₹{result[2]}")

    def view_transactions(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT transaction_type, amount, transaction_date FROM transactions WHERE account_no = %s", (self.account_no,))
        records = cur.fetchall()
        conn.close()
        if not records:
            messagebox.showinfo("Transactions", "No transactions found.")
        else:
            data = "\n".join([f"{r[0]} - ₹{r[1]} on {r[2]}" for r in records])
            messagebox.showinfo("Transaction History", data)

# ---------- LOGIN SCREEN ----------
class LoginApp:
    def __init__(self, master):
        self.master = master
        self.master.title("ATM Login")
        self.master.geometry("350x250")

        tk.Label(master, text="ATM Login", font=("Arial", 16, "bold")).pack(pady=10)
        tk.Label(master, text="Account Number:").pack()
        self.acc_entry = tk.Entry(master)
        self.acc_entry.pack(pady=5)

        tk.Label(master, text="PIN:").pack()
        self.pin_entry = tk.Entry(master, show="*")
        self.pin_entry.pack(pady=5)

        tk.Button(master, text="Login", command=self.login).pack(pady=10)
        tk.Button(master, text="Exit", command=master.quit).pack()

    def login(self):
        acc_no = self.acc_entry.get()
        pin = self.pin_entry.get()
        
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM accounts WHERE account_no = %s AND pin = %s", (acc_no, pin))
        result = cur.fetchone()
        conn.close()

        if result:
            messagebox.showinfo("Login Successful", f"Welcome {result[1]}!")
            self.master.destroy()
            root = tk.Tk()
            ATMApp(root, acc_no)
            root.mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid Account Number or PIN")

# ---------- MAIN PROGRAM ----------
if __name__ == "__main__":
    window = tk.Tk()
    LoginApp(window)
    window.mainloop()
