import pandas as pd
from io import StringIO
import sqlite3
import re
import tkinter as tk
from tkinter import filedialog, Label, Text, Button
import requests
import os
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

# Function to get AI response


def get_ai_response(user_input):
    print(user_input)
    url = "https://chatgptapi-2pc2.onrender.com/"
    data = {
        "model_role": "You are a helpful assistant for writing a SQL Query of given dataset and by default table name is 'dataset'. and each query will end with a semicolon",
        "user_message": user_input
    }
    response = requests.post(url, json=data)
    response_json = response.json()
    print("Response: ", response_json["answer"])
    return response_json["answer"]

# Function to handle query and display result


def handle_query():
    user_input = text.get("1.0", 'end-1c')
    user_query = user_input.strip()

    if user_query:
        lines = csv_data.split("\n")
        Ai_csv_data = "\n".join(lines[:15])
        AiQuery = get_ai_response(Ai_csv_data + "\n\n\n Query: " + user_query)
        AiQuerytry = AiQuery
        sql_query_match = re.search(r'SELECT .*?;', AiQuery, re.DOTALL)
        if sql_query_match:
            AiQuery = sql_query_match.group().strip()
            result_text.config(state='normal')
            result_text.delete(1.0, "end")
            result_text.insert(
                tk.END, f"\n-----------------------\n{AiQuery}\n-----------------------\n\n")
            result_text.config(state='disabled')

            try:
                df = pd.read_csv(StringIO(csv_data))
                conn = sqlite3.connect(':memory:')
                df.to_sql('dataset', conn, index=False, if_exists='replace')
                result = pd.read_sql_query(AiQuery, conn)
                result_text.config(state='normal')
                result_text.insert(tk.END, f"{result}\n")
                result_text.config(state='disabled')
                conn.close()
            except Exception as e:
                result_text.config(state='normal')
                result_text.delete(1.0, "end")
                result_text.insert(tk.END, f"Error: {e}\n")
                result_text.config(state='disabled')

        else:
            result_text.config(state='normal')
            result_text.delete(1.0, "end")
            result_text.insert(
                tk.END, f"{AiQuerytry}\n\nSQL query not found in the provided text.\n")
            result_text.config(state='disabled')


# Function to open file dialog and set CSV data
def open_file_dialog():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        global csv_data
        with open(file_path, 'r') as file:
            csv_data = file.read()
        file_label.config(text=f"File: {os.path.basename(file_path)}")


# GUI Setup
root = tk.Tk()
root.title("SQL Query Assistant")

# Open File Button
open_file_button = Button(root, text="Upload CSV File",
                          command=open_file_dialog)
open_file_button.pack(pady=10)

# File Label
file_label = Label(root, text="")
file_label.pack()

# Query Input Textbox
text = Text(root, height=10, width=50)
text.pack(pady=10)

# Query Button
query_button = Button(root, text="Run Query", command=handle_query)
query_button.pack()

# Result Textbox
result_text = Text(root, height=100, width=150)
result_text.pack(pady=10)
result_text.config(state='disabled')

# Run GUI
root.mainloop()
