import streamlit as st
import pandas as pd

# Title of the web application
st.title('Excel File Upload and Analysis')

# File uploader allows user to add their own Excel file
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

# Function to format description with <br> tags
def format_description(description):
    # Replace each newline character with <br><br> and avoid duplicates
    return '<br><br>'.join(filter(None, description.split('\n')))

# Function to strip leading bullet points from dot points
def strip_bullet_points(text):
    # Define characters to strip from the beginning of the string
    characters_to_strip = '•*- '
    return text.lstrip(characters_to_strip)

# Function to generate the HTML structure from a row of dataframe
def generate_html(row_data):
    description = format_description(row_data['Description'])
    html_template = f"""
    {description}
    <br><br>
    <ul>
        <li>{strip_bullet_points(row_data['Dot Point 2'])}</li>
        <li>{strip_bullet_points(row_data['Dot Point 3'])}</li>
        <li>{strip_bullet_points(row_data['Dot Point 5'])}</li>
        <li>{strip_bullet_points(row_data['Dot Point 6'])}</li>
        <li>{strip_bullet_points(row_data['Dot Point 7'])}</li>
        <li>{strip_bullet_points(row_data['Dot Point 8'])}</li>
        <li>{strip_bullet_points(row_data['Dot Point 4'])}</li>
        <li>{strip_bullet_points(row_data['Dot Point 1'])}</li>
    </ul>
    """
    return html_template.strip()

# The Excel file is read into a dataframe and displayed
if uploaded_file is not None:
    # Convert the uploaded Excel file to a dataframe
    df = pd.read_excel(uploaded_file)

    # Convert dataframe rows to dictionaries and generate HTML for one row as an example
    rows = df.to_dict('records')
    example_html_content = generate_html(rows[0])  # assuming the Excel has the necessary columns
    st.write(example_html_content, unsafe_allow_html=True)

    # Other actions with the dataframe can be added here