import streamlit as st

# Title of the web application
st.title('CSV File Upload and Access')

# File uploader allows user to add their own CSV
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

# The CSV is read into a dataframe and displayed
if uploaded_file is not None:


    # Now you can access the `data` variable programmatically
    # For example, let's say you want to show the first 5 rows of the dataframe
    st.write("Displaying the first 5 rows of the dataframe:")
  

    # Perform other actions with the dataframe here
    # ...