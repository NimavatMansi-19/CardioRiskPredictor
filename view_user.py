import sqlite3
import pandas as pd

# Connect to the database file
conn = sqlite3.connect('users.db')

# Read the data into a Pandas DataFrame
df = pd.read_sql_query("SELECT * FROM userstable", conn)

print("--- REGISTERED USERS ---")
print(df)

conn.close()