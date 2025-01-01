import sqlite3

def extract_pdf_data(db_file):
    """
    Extracts PDF data from the SQLite database.

    Args:
        db_file (str): Path to the SQLite database file.

    Returns:
        list: A list of tuples, where each tuple contains the ID and PDF data.
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute("SELECT id, pdf_blob FROM pdf_data")
    rows = cursor.fetchall()

    conn.close()
    return rows


# Example usage:
db_file = 'my_database.db'

pdf_data = extract_pdf_data(db_file)

# Process the extracted data
for row in pdf_data:
    pdf_id, pdf_blob = row
    # Process PDF data (e.g., save to a file)
    with open(f"extracted_pdf_{pdf_id}.pdf", "wb") as f:
        f.write(pdf_blob)
