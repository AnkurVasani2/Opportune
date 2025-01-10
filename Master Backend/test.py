import sqlite3

def check_pdf_data(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pdf_data")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    conn.close()

# Specify your database file
db_file = 'my_database.db'
check_pdf_data(db_file)
