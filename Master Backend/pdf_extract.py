import sqlite3
import PyPDF2
import re
import string
import os

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

def extract_technical_words(pdf_path):
    """
    Extracts technical words from a PDF file and creates a dictionary 
    of unique words along with their counts.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        A dictionary where keys are unique technical words 
        and values are their counts.
    """

    try:
        # Open the PDF file in read-binary mode
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            # Initialize an empty list to store all text from the PDF
            all_text = ""

            # Iterate through each page of the PDF and extract text
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                all_text += page_text

        # Clean the text by removing punctuation and converting to lowercase
        clean_text = all_text.translate(str.maketrans('', '', string.punctuation)).lower()

        # Define a regular expression to match potential technical words
        # This regex can be adjusted based on your specific needs
        # For example, to include numbers or hyphens, modify the pattern accordingly
        pattern = r"\b(?:[A-Za-z]{3,}|[A-Za-z]{2}[A-Z]|[A-Z]{2}[a-z])\b"  # Match words with at least 3 letters

        # Find all matching words
        words = re.findall(pattern, clean_text)

        # Create a dictionary to store word counts
        word_counts = {}
        for word in words:
            if word in word_counts:
                word_counts[word] += 1
            else:
                word_counts[word] = 1

        return word_counts

    except Exception as e:
        print(f"An error occurred: {e}")
        return {}

# Example usage:
db_file = 'my_database.db'

pdf_data = extract_pdf_data(db_file)

technical_word_counts = {}
# Process the extracted data
for row in pdf_data:
    pdf_id, pdf_blob = row
    #print(f"--------------------------------------------------------------------------------------{pdf_id}")
    # Process PDF data (e.g., save to a file)
    with open(f"extracted_pdf_{pdf_id}.pdf", "wb") as f:
        f.write(pdf_blob)
        pdf_file_path = f"extracted_pdf_{pdf_id}.pdf"
        individual_word_counts = extract_technical_words(pdf_file_path)
        technical_word_counts.update(individual_word_counts)
    os.remove(f"extracted_pdf_{pdf_id}.pdf")

def reverse_sort_map_by_value(my_map):
  """
  Sorts a dictionary by its values in descending order.

  Args:
    my_map: The dictionary to be sorted.

  Returns:
    A new dictionary with the same keys and values as the input dictionary, 
    but sorted by the values in descending order.
  """
  return dict(sorted(my_map.items(), key=lambda item: item[1], reverse=True))

def remove_keys_with_value_1(my_dict):
  """
  Removes all keys from a dictionary that have a value of 1.

  Args:
    my_dict: The dictionary to be modified.

  Returns:
    The modified dictionary with keys having value 1 removed.
  """
  keys_to_remove = [key for key, value in my_dict.items() if value == 1]
  for key in keys_to_remove:
    my_dict.pop(key)
  return my_dict

technical_word_counts = reverse_sort_map_by_value(technical_word_counts)
technical_word_counts = remove_keys_with_value_1(technical_word_counts)

#words = []

for word, count in technical_word_counts.items():
    #words.append(word)
    print(f"{word}: {count}")
