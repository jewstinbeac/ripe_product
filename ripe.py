import streamlit as st
import pandas as pd
import openai
import random
import time
from tempfile import NamedTemporaryFile

# Title of the web application
st.title('Ripe Product Descriptionizer 🍒')
st.write('made with ❤️ by raava')

# Input field for the user to enter their API key
api_key = st.text_input("Enter your OpenAI API key")

# File uploader allows user to add their own Excel file
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

# define a retry decorator
def retry_with_exponential_backoff(
    func,
    initial_delay: float = 1,
    exponential_base: float = 2,
    jitter: bool = True,
    max_retries: int = 20,
    errors: tuple = (openai.RateLimitError,),
):
    """Retry a function with exponential backoff."""

    def wrapper(*args, **kwargs):
        # Initialize variables
        num_retries = 0
        delay = initial_delay

        # Loop until a successful response or max_retries is hit or an exception is raised
        while True:
            try:
                return func(*args, **kwargs)

            # Retry on specified errors
            except errors as e:
                # Increment retries
                num_retries += 1

                # Check if max retries has been reached
                if num_retries > max_retries:
                    raise Exception(
                        f"Maximum number of retries ({max_retries}) exceeded."
                    )

                # Increment the delay
                delay *= exponential_base * (1 + jitter * random.random())

                # Sleep for the delay
                time.sleep(delay)

            # Raise exceptions for any errors not specified
            except Exception as e:
                raise e

    return wrapper

@retry_with_exponential_backoff
def chat_with_gpt4(prompt, model="gpt-4", max_tokens=200):
    openai.api_key = api_key
    
    response = openai.chat.completions.create(
        model=model,
        messages=[
                {"role": "system", "content": "You are generating product descriptions based on individuals details of garments, these descriptions are roughly 400 characters."},
                {"role": "user", "content": prompt},
                ],
        max_tokens=max_tokens
    )
    return response.choices[0].message.content.strip()


def generate_description(product_name, dp_1=None, dp_2=None, dp_3=None, dp_4=None,
                         dp_5=None, dp_6=None, dp_7=None, dp_8=None):
    # Clean + compact details for the model (helps prevent rambling)
    details = [dp_1, dp_2, dp_3, dp_4, dp_5, dp_6, dp_7, dp_8]
    details = [str(d).strip().lstrip("•").strip() for d in details if d and str(d).strip()]
    details_block = "\n".join(f"- {d}" for d in details)

    desc_prompt = f"""
    You are writing a Ripe product description.
    
    VOICE + TONE (must follow)
    - Warm & human, like a trusted friend. Clear, calm, direct. Nurturing and reassuring. Confident and polished, never intimidating. :contentReference[oaicite:4]{index=4}
    - Always warm, conversational, nurturing, with a stylish edge. :contentReference[oaicite:5]{index=5}
    - Keep it simple, caring, genuine. No hard-sell hype, no jargon. :contentReference[oaicite:6]{index=6}
    
    STYLE RULES
    - Short, clear sentences. Use contractions. Prefer no emoji. :contentReference[oaicite:7]{index=7}
    - When in doubt: simplify and soften. :contentReference[oaicite:8]{index=8}
    
    WORDS TO LEAN ON (use 1–2 max, naturally)
    - your go-to, made to live in, wear it on repeat, easy does it :contentReference[oaicite:9]{index=9}
    - soft on skin, made to grow with you, designed to support, for every stage :contentReference[oaicite:10]{index=10}
    - comfort-first, everyday ease, made for now and later, quietly confident :contentReference[oaicite:11]{index=11}
    
    GENTLE CTA (end with one, no pressure)
    - ready when you are / take a closer look / explore more :contentReference[oaicite:12]{index=12}
    
    AVOID (never use)
    - hurry, last chance, don’t miss out, shop now :contentReference[oaicite:13]{index=13}
    - game-changer, must-have, revolutionary, disruptive, curated edit :contentReference[oaicite:14]{index=14}
    - value-add, solutions, leverage, synergy :contentReference[oaicite:15]{index=15}
    
    OUTPUT REQUIREMENTS (follow exactly)
    - Write ONE description only (no headings, no quotes, no bullet points).
    - 2–3 short sentences, 380–420 characters (including spaces).
    - Do NOT mention measurements/lengths.
    - Only claim features that appear in the details (e.g., nursing friendly, adjustable waist, buttons).
    - Include: (1) fabric/feel, (2) 2 key design features, (3) 1 simple styling suggestion, (4) gentle CTA at the end.
    
    PRODUCT INPUT
    Name: {product_name}
    Details:
    {details_block}
    """.strip()

    return chat_with_gpt4(desc_prompt)


def format_description(description):
    return '<br><br>'.join(filter(None, description.split('\n')))

def strip_bullet_points(text):
    text = str(text)
    characters_to_strip = '•*- '
    return text.lstrip(characters_to_strip)

def convert_care_to_html(text):
    text = str(text)
    lines = text.split('\n')
    html_lines = [f"<li>{line.strip()}</li>" for line in lines if line.strip()]
    return "<ul>\n" + "\n".join(html_lines) + "\n</ul>"

def generate_html(row_data, description):
    description = format_description(description)

    care_instructions = convert_care_to_html(row_data['Care Instructions'])
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
    {care_instructions}
    """
    return html_template.strip()

def process_row(row, style_descriptions, style_htmls):
    style_code = row['Style Code']
    product_name = row['Product Name']
    colour_code = row['Colour Code']
    colour_name = row['Colour Name']
    dp_1 = row['Dot Point 1']
    dp_2 = row['Dot Point 2']
    dp_3 = row['Dot Point 3']
    dp_4 = row['Dot Point 4']
    dp_5 = row['Dot Point 5']
    dp_6 = row['Dot Point 6']
    dp_7 = row['Dot Point 7']
    dp_8 = row['Dot Point 8']

    point_list = [dp_1,dp_2, dp_3, dp_4, dp_5, dp_6, dp_7, dp_8]
    print(point_list)

    if any(str(point) == 'nan' for point in point_list):
        description = ''
        html = ''
        st.write('empty row')
    elif style_code not in style_descriptions:
        description = generate_description(product_name, dp_1, dp_2, dp_3, dp_4, dp_5, dp_6, dp_7, dp_8)
        html = generate_html(row, description)
        style_descriptions[style_code] = description
        style_htmls[style_code] = description
        st.subheader(style_code + ' ' + product_name)
        st.write('---------------')
        st.write('Description')
        st.write('---------------')
        st.write(description)
        st.write('---------------')
        st.write('HTML')
        st.write('---------------')
        st.code(html)
    else:
        description = style_descriptions[style_code]
        html = style_htmls[style_code]

    return description, html

def process_dataframe(df):
    descriptions = []
    htmls = []
    style_descriptions = {}
    style_htmls = {}

    for index, row in df.iterrows():
        description, html = process_row(row, style_descriptions, style_htmls)
        descriptions.append(description)
        htmls.append(html)

    return descriptions, htmls

if uploaded_file is not None:
    workbook = pd.ExcelFile(uploaded_file)

    with st.form(key='form_select'):
        sheet_name = st.selectbox("Select a sheet", workbook.sheet_names)
        submit_button = st.form_submit_button(label='Do it :)')

    if submit_button:
        df = pd.read_excel(workbook, sheet_name=sheet_name)
        descriptions, htmls = process_dataframe(df)

        data = {'Generated Descriptions': descriptions, 'Generated HTMLs': htmls}
        new_df = pd.DataFrame(data)

        with NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            new_df.to_excel(tmp.name, index=False)
            tmp.seek(0)
            data = tmp.read()
            st.sidebar.download_button(
                label="Download Sheet with descriptions and HTML",
                data=data,
                file_name='db_with_descriptions.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )


 
