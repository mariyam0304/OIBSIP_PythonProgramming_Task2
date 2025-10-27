import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime

# -----------------------------
# DATABASE SETUP
# -----------------------------
def init_db():
    """Initialize SQLite database and create table if not exists."""
    try:
        conn = sqlite3.connect("bmi_data.db")
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS bmi_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            weight REAL,
            height REAL,
            bmi REAL,
            category TEXT,
            date TEXT
        )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", f"Error initializing database:\n{e}")

# -----------------------------
# BMI CALCULATION FUNCTION
# -----------------------------
def calculate_bmi():
    """Calculate BMI and store result."""
    username = entry_name.get().strip()
    try:
        weight = float(entry_weight.get())
        height = float(entry_height.get())
        if weight <= 0 or height <= 0:
            raise ValueError("Invalid values")
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid positive numbers for weight and height.")
        return

    bmi = weight / (height ** 2)
    category = classify_bmi(bmi)

    try:
        conn = sqlite3.connect("bmi_data.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO bmi_records (username, weight, height, bmi, category, date) VALUES (?, ?, ?, ?, ?, ?)",
                       (username, weight, height, bmi, category, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", f"Error saving data:\n{e}")
        return

    result_label.config(text=f"{username}, your BMI is {bmi:.2f} ({category}).", fg="#2E8B57")
    entry_weight.delete(0, tk.END)
    entry_height.delete(0, tk.END)

def classify_bmi(bmi):
    """Return BMI category."""
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 24.9:
        return "Normal weight"
    elif 25 <= bmi < 29.9:
        return "Overweight"
    else:
        return "Obese"

# -----------------------------
# VIEW HISTORY
# -----------------------------
def view_history():
    username = entry_name.get().strip()
    if not username:
        messagebox.showwarning("Missing Info", "Please enter your name first.")
        return

    try:
        conn = sqlite3.connect("bmi_data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT date, bmi, category FROM bmi_records WHERE username=? ORDER BY date", (username,))
        records = cursor.fetchall()
        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", f"Error retrieving history:\n{e}")
        return

    if not records:
        messagebox.showinfo("No Data", "No BMI records found for this user.")
        return

    # Display records
    hist_window = tk.Toplevel(root)
    hist_window.title(f"{username}'s BMI History")
    hist_window.geometry("450x300")

    tree = ttk.Treeview(hist_window, columns=("Date", "BMI", "Category"), show="headings")
    tree.heading("Date", text="Date")
    tree.heading("BMI", text="BMI")
    tree.heading("Category", text="Category")
    for r in records:
        tree.insert("", tk.END, values=(r[0], f"{r[1]:.2f}", r[2]))
    tree.pack(expand=True, fill="both")

# -----------------------------
# PLOT TREND GRAPH
# -----------------------------
def show_graph():
    username = entry_name.get().strip()
    if not username:
        messagebox.showwarning("Missing Info", "Please enter your name first.")
        return

    try:
        conn = sqlite3.connect("bmi_data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT date, bmi FROM bmi_records WHERE username=? ORDER BY date", (username,))
        records = cursor.fetchall()
        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", f"Error fetching graph data:\n{e}")
        return

    if not records:
        messagebox.showinfo("No Data", "No BMI data to display.")
        return

    dates = [r[0] for r in records]
    bmis = [r[1] for r in records]

    plt.figure(figsize=(7, 4))
    plt.plot(dates, bmis, marker='o', color='teal', linewidth=2)
    plt.title(f"BMI Trend for {username}")
    plt.xlabel("Date")
    plt.ylabel("BMI")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# -----------------------------
# GUI DESIGN
# -----------------------------
root = tk.Tk()
root.title("Smart BMI Tracker")
root.geometry("450x450")
root.config(bg="#EAF6F6")

tk.Label(root, text="💪 Smart BMI Tracker", font=("Comic Sans MS", 18, "bold"), fg="#2E8B57", bg="#EAF6F6").pack(pady=15)

tk.Label(root, text="Enter Name:", bg="#EAF6F6").pack()
entry_name = tk.Entry(root, width=35)
entry_name.pack(pady=2)

tk.Label(root, text="Enter Weight (kg):", bg="#EAF6F6").pack()
entry_weight = tk.Entry(root, width=35)
entry_weight.pack(pady=2)

tk.Label(root, text="Enter Height (m):", bg="#EAF6F6").pack()
entry_height = tk.Entry(root, width=35)
entry_height.pack(pady=2)

tk.Button(root, text="Calculate BMI", command=calculate_bmi, bg="#32CD32", fg="white", width=25).pack(pady=8)
tk.Button(root, text="View History", command=view_history, bg="#1E90FF", fg="white", width=25).pack(pady=8)
tk.Button(root, text="Show Trend Graph", command=show_graph, bg="#FF8C00", fg="white", width=25).pack(pady=8)

result_label = tk.Label(root, text="", font=("Arial", 11), bg="#EAF6F6")
result_label.pack(pady=10)

tk.Button(root, text="Exit", command=root.destroy, bg="#DC143C", fg="white", width=25).pack(pady=8)

# Initialize DB and start app
init_db()
root.mainloop()
