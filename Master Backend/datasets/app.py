import pandas as pd

# Function to transform the level values
def transform_level(level):
    if level == "All Levels":
        return "intermediate"
    elif level == "Beginner Level":
        return "beginner"
    elif level == "Intermediate Level":
        return "intermediate"
    elif level == "Expert Level":
        return "advanced"
    else:
        return level

# Load the input CSV file
input_csv = "udemy_course_data.csv"  # Replace with your actual input file path
output_csv = "output.csv"  # Replace with your desired output file path

# Read the CSV
df = pd.read_csv(input_csv)

# Rename columns
df.rename(columns={
    "course_title": "Name",
    "url": "Link",
    "level": "level",
    "subject": "About"
}, inplace=True)

# Set "University" as "Udemy" for all rows
df["University"] = "Udemy"

# Transform the level column
df["level"] = df["level"].apply(transform_level)

# Select only the required columns
output_df = df[["Name", "University", "level", "Link", "About"]]

# Save the transformed data to a new CSV
output_df.to_csv(output_csv, index=False)

print(f"Transformed CSV saved to {output_csv}")
