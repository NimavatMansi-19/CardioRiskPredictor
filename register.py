import gspread
from oauth2client.service_account import ServiceAccountCredentials
import bcrypt

# 1. SETUP CONNECTION
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# 2. OPEN SHEET
try:
    sheet = client.open("CardioUsers").sheet1
except Exception as e:
    print("Error: Could not find Google Sheet 'CardioUsers'. Make sure you created it and shared it with the bot email.")
    exit()

# 3. FIX MISSING COLUMNS AUTOMATCIALLY
# If the first row is empty or wrong, this adds headers
if sheet.row_values(1) != ['Email', 'Password']:
    print("⚠️ Columns missing. Adding 'Email' and 'Password' headers...")
    sheet.delete_rows(1) # Clean up if needed
    sheet.insert_row(['Email', 'Password'], 1)

# 4. REGISTER USER
email = input("Enter new user email: ")
password = input("Enter new password: ")

hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
sheet.append_row([email, hashed_password])

print(f"✅ Success! User {email} added. You can now login.")
