import tkinter as tk
from tkinter import messagebox
import mysql.connector
import random

# ---------- DATABASE CONNECTION ----------
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",              # change if needed
        password="07Dec@",        # 🔹 replace with your MySQL password
        database="atm_system"
    )

# ---------- ATM MAIN WINDOW ----------
class ATMApp:
    def __init__(self, master, account_no):
        self.master = master
        self.account_no = account_no
        self.master.title("ATM Machine System")
        self.master.geometry("400x500")
        self.master.resizable(False, False)

        tk.Label(master, text="ATM Operations", font=("Arial", 18, "bold")).pack(pady=15)

        tk.Button(master, text="Deposit", width=20, command=self.deposit).pack(pady=8)
        tk.Button(master, text="Withdraw", width=20, command=self.withdraw).pack(pady=8)
        tk.Button(master, text="Check Balance", width=20, command=self.check_balance).pack(pady=8)
        tk.Button(master, text="View Transactions", width=20, command=self.view_transactions).pack(pady=8)
        tk.Button(master, text="Change PIN", width=20, command=self.change_pin).pack(pady=8)
        tk.Button(master, text="Delete Account", width=20, command=self.delete_account).pack(pady=8)
        tk.Button(master, text="Exit", width=20, command=master.quit).pack(pady=15)

    # ---------- DEPOSIT ----------

    def deposit(self):
        deposit_window = tk.Toplevel(self.master)
        deposit_window.title("Deposit Money")
        deposit_window.geometry("300x200")

        tk.Label(deposit_window, text="Enter amount to deposit:").pack(pady=10)
        amount_entry = tk.Entry(deposit_window)
        amount_entry.pack(pady=5)

        def confirm_deposit():
            try:
                amount = float(amount_entry.get())
                if amount <= 0:
                    messagebox.showwarning("Invalid Amount", "Amount must be positive.")
                    return

                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO transactions (account_no, transaction_type, amount) VALUES (%s, 'Deposit', %s)",
                    (self.account_no, amount)
                )
                cur.execute("UPDATE accounts SET balance = balance + %s WHERE account_no = %s", (amount, self.account_no))
                conn.commit()
                conn.close()
                messagebox.showinfo("Deposit Successful", f"₹{amount:.2f} deposited successfully!")
                deposit_window.destroy()
            except ValueError:
                messagebox.showwarning("Invalid Input", "Please enter a valid number.")

        tk.Button(deposit_window, text="Deposit", command=confirm_deposit).pack(pady=10)


    # ---------- WITHDRAW ----------
    
    def withdraw(self):
        withdraw_window = tk.Toplevel(self.master)
        withdraw_window.title("Withdraw Money")
        withdraw_window.geometry("300x200")

        tk.Label(withdraw_window, text="Enter amount to withdraw:").pack(pady=10)
        amount_entry = tk.Entry(withdraw_window)
        amount_entry.pack(pady=5)

        def confirm_withdraw():
            try:
                amount = float(amount_entry.get())
                if amount <= 0:
                    messagebox.showwarning("Invalid Amount", "Amount must be positive.")
                    return

                conn = get_connection()
                cur = conn.cursor()
                cur.execute("SELECT balance FROM accounts WHERE account_no = %s", (self.account_no,))
                balance = cur.fetchone()[0]

                if amount > balance:
                    messagebox.showwarning("Insufficient Funds", "Not enough balance to withdraw.")
                else:
                    cur.execute(
                        "INSERT INTO transactions (account_no, transaction_type, amount) VALUES (%s, 'Withdraw', %s)",
                        (self.account_no, amount)
                    )
                    cur.execute("UPDATE accounts SET balance = balance - %s WHERE account_no = %s", (amount, self.account_no))
                    conn.commit()
                    messagebox.showinfo("Withdrawal Successful", f"₹{amount:.2f} withdrawn successfully!")
                    withdraw_window.destroy()
                conn.close()
            except ValueError:
                messagebox.showwarning("Invalid Input", "Please enter a valid number.")

        tk.Button(withdraw_window, text="Withdraw", command=confirm_withdraw).pack(pady=10)

    # ---------- CHECK BALANCE ----------
    def check_balance(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT holder_name, bank_name, balance FROM accounts WHERE account_no = %s", (self.account_no,))
        result = cur.fetchone()
        conn.close()

        messagebox.showinfo(
            "Account Balance",
            f"Name: {result[0]}\nBank: {result[1]}\nBalance: ₹{result[2]:.2f}"
        )

    # ---------- VIEW TRANSACTIONS ----------
    def view_transactions(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT transaction_type, amount, transaction_date FROM transactions WHERE account_no = %s ORDER BY transaction_date DESC",
            (self.account_no,)
        )
        records = cur.fetchall()
        conn.close()

        if not records:
            messagebox.showinfo("Transactions", "No transactions found.")
        else:
            data = "\n".join([f"{r[0]} - ₹{r[1]} on {r[2]}" for r in records])
            messagebox.showinfo("Transaction History", data)

    # ---------- CHANGE PIN ----------
    def change_pin(self):
        def submit_pin():
            old_pin = old_pin_entry.get()
            new_pin = new_pin_entry.get()
            if not (old_pin and new_pin):
                messagebox.showwarning("Error", "Both fields are required!")
                return
            if len(new_pin) != 4 or not new_pin.isdigit():
                messagebox.showwarning("Error", "New PIN must be 4 digits!")
                return

            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT pin FROM accounts WHERE account_no = %s", (self.account_no,))
            current_pin = cur.fetchone()[0]

            if old_pin != current_pin:
                messagebox.showerror("Error", "Old PIN is incorrect!")
                conn.close()
                return

            cur.execute("UPDATE accounts SET pin = %s WHERE account_no = %s", (new_pin, self.account_no))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "PIN changed successfully!")
            pin_window.destroy()

        pin_window = tk.Toplevel(self.master)
        pin_window.title("Change PIN")
        pin_window.geometry("300x200")

        tk.Label(pin_window, text="Old PIN:").pack(pady=5)
        old_pin_entry = tk.Entry(pin_window, show="*")
        old_pin_entry.pack(pady=5)

        tk.Label(pin_window, text="New PIN:").pack(pady=5)
        new_pin_entry = tk.Entry(pin_window, show="*")
        new_pin_entry.pack(pady=5)

        tk.Button(pin_window, text="Submit", command=submit_pin).pack(pady=10)

    # ---------- DELETE ACCOUNT ----------
    def delete_account(self):
        confirm = messagebox.askyesno(
            "Confirm Delete", "Are you sure you want to delete your account? This cannot be undone!"
        )
        if confirm:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM transactions WHERE account_no = %s", (self.account_no,))
            cur.execute("DELETE FROM accounts WHERE account_no = %s", (self.account_no,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Deleted", "Your account has been deleted successfully!")
            self.master.destroy()

# ---------- ACCOUNT CREATION ----------
class CreateAccountApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Create New Account")
        self.master.geometry("400x350")
        self.master.resizable(False, False)

        tk.Label(master, text="Create New Account", font=("Arial", 16, "bold")).pack(pady=15)

        tk.Label(master, text="Full Name:").pack()
        self.name_entry = tk.Entry(master)
        self.name_entry.pack(pady=5)

        tk.Label(master, text="Bank Name:").pack()
        self.bank_entry = tk.Entry(master)
        self.bank_entry.pack(pady=5)

        tk.Label(master, text="Set PIN (4 digits):").pack()
        self.pin_entry = tk.Entry(master, show="*")
        self.pin_entry.pack(pady=5)

        tk.Label(master, text="Initial Deposit:").pack()
        self.deposit_entry = tk.Entry(master)
        self.deposit_entry.pack(pady=5)

        tk.Button(master, text="Create Account", command=self.create_account).pack(pady=10)
        tk.Button(master, text="Back to Login", command=self.back_to_login).pack()

    def create_account(self):
        name = self.name_entry.get()
        bank = self.bank_entry.get()
        pin = self.pin_entry.get()
        deposit = self.deposit_entry.get()

        if not (name and bank and pin and deposit):
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        if len(pin) != 4 or not pin.isdigit():
            messagebox.showwarning("Invalid PIN", "PIN must be 4 digits.")
            return

        try:
            deposit = float(deposit)
        except ValueError:
            messagebox.showwarning("Invalid Input", "Deposit must be a number.")
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO accounts (holder_name, bank_name, balance, pin) VALUES (%s, %s, %s, %s)",
            (name, bank, deposit, pin)
        )
        conn.commit()
        account_no = cur.lastrowid
        conn.close()

        messagebox.showinfo("Account Created", f"Account created successfully!\nYour Account No: {account_no}")
        self.master.destroy()
        root = tk.Tk()
        LoginApp(root)
        root.mainloop()

    def back_to_login(self):
        self.master.destroy()
        root = tk.Tk()
        LoginApp(root)
        root.mainloop()

# ---------- LOGIN ----------
class LoginApp:
    def __init__(self, master):
        self.master = master
        self.master.title("ATM Login")
        self.master.geometry("350x300")
        self.master.resizable(False, False)

        tk.Label(master, text="ATM Login", font=("Arial", 16, "bold")).pack(pady=15)
        tk.Label(master, text="Account Number:").pack()
        self.acc_entry = tk.Entry(master)
        self.acc_entry.pack(pady=5)

        tk.Label(master, text="PIN:").pack()
        self.pin_entry = tk.Entry(master, show="*")
        self.pin_entry.pack(pady=5)

        tk.Button(master, text="Login", command=self.login).pack(pady=10)
        tk.Button(master, text="Create New Account", command=self.open_create_account).pack()
        tk.Button(master, text="Exit", command=master.quit).pack(pady=10)

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

    def open_create_account(self):
        self.master.destroy()
        root = tk.Tk()
        CreateAccountApp(root)
        root.mainloop()

# ---------- MAIN ----------
if __name__ == "__main__":
    window = tk.Tk()
    LoginApp(window)
    window.mainloop()
