import urllib.request
import os

print("Downloading the official Chinook Database...")

url = "https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite"
db_path = "../data/chinook.db"

# Download and save the file
urllib.request.urlretrieve(url, db_path)

print(f"Success! Saved real-world testing database to: {db_path}")