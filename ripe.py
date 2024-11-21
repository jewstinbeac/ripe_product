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
def chat_with_gpt4(prompt, model="gpt-4o", max_tokens=200):
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


def generate_description(product_name, dp_1, dp_2, dp_3, dp_4, dp_5, dp_6, dp_7='', dp_8=''):
    desc_prompt = f"""
    Examples:

    Example 1:
    
    "Embrace effortless elegance with the Nala Knot Front Knit. This comfy go-to staple features a semi-fitted, fully fashioned knit design with a chic crossover that adds a pop of character. The generous V-neckline, cropped length, and long sleeves make it the perfect layering piece you'll reach for time and time again—pairing easily with skirts, dresses, and high-waisted pants."
    
    Example 2:
    
    "Step into the season with the Marni Mesh Skirt, crafted from a beautiful print mesh jersey that feels like wearing nothing at all. Designed with an elastic waistband for maximum comfort, this midi skirt features a straight silhouette that skims your body and a side split for added flair. Pair it with our Jodie Ruched Rib Tank for an effortlessly cool ensemble, or throw on your favorite knitwear for a versatile, all-season essential."

    Instructions:
    
    Please generate a product description that emulates the tone and style of the examples provided, aiming for a blend of descriptive elegance, practical detailing, and lifestyle integration.
    
    Your description should:
    
    Start with an Engaging Hook:
    
    Begin with a captivating sentence that highlights a standout feature of the product.
    Use compelling adjectives and phrases to immediately draw the reader in.
    Example: "Embrace effortless elegance with our..."
    Highlight the Fabric and Feel:
    
    Describe the material using sensory language that evokes touch and comfort.
    Mention the quality, texture, and any special characteristics of the fabric.
    Convey how the fabric feels against the skin (e.g., "buttery soft," "lightweight and breathable").
    Emphasize any benefits like stretch, warmth, or breathability.
    Detail Key Design Features:
    
    Specify elements that add to both functionality and style.
    Mention neckline styles, sleeve lengths, closures, patterns, or unique embellishments.
    Highlight features that make the garment stand out (e.g., "elegant drape," "sleek silhouette").
    Include any design details that are fashionable or on-trend.
    Emphasize Functionality:
    
    Point out features that cater to maternity needs, such as nursing access, adjustable fits, or comfort-enhancing elements.
    Use phrases that directly address the needs of expecting or nursing mothers.
    Example: "Thoughtfully designed with discreet nursing access for your convenience."
    Set the Scene:
    
    Suggest specific occasions or settings where the garment would be ideal.
    Encourage the reader to envision themselves wearing the product in various scenarios.
    Examples: "Perfect for weekend brunches," "An elegant choice for your baby shower."
    Offer Styling Suggestions:
    
    Provide tips on how to style the garment with other items or accessories.
    Suggest complementary pieces or layering options (e.g., "Pair with a cozy cardigan," "Style with ankle boots for a chic look").
    Mention how the garment can transition between casual and dressy occasions.
    Use Emotive and Sensory Language:
    
    Incorporate words that appeal to emotions and senses to create a vivid image.
    Use phrases that evoke feelings of confidence, elegance, or comfort.
    Example: "Feel effortlessly radiant as you..."
    Highlight Versatility and Transition:
    
    Emphasize how the garment adapts through different stages of maternity and beyond.
    Point out its suitability for various times of the day or seasons.
    Use phrases like "from day to night" or "a timeless piece for every trimester."
    Ensure Clarity and Flow:
    
    Write sentences that are clear, concise, and easy to understand.
    Maintain a smooth narrative that connects ideas logically.
    Avoid overly complex language or industry jargon.
    Important Guidelines:
    
    Do not reference numerical lengths or measurements of the garment. Focus on qualitative descriptions instead.
    Keep your description to approximately 400 characters to maintain conciseness and readability.
    Use a warm, inviting, and aspirational tone, matching the style of the provided examples.
    Avoid using bullet points or lists in the description; write in full sentences and cohesive paragraphs.
    Integrate the product details seamlessly into the description without explicitly listing them.
    Ensure the description is unique and original, not copied from the examples.
    Please generate a description for the following product details:
    
    Product Name: {product_name}
    Details:
    {dp_1}
    {dp_2}
    {dp_3}
    {dp_4}
    {dp_5}
    {dp_6}
    {dp_7}
    {dp_8}
    """

    return chat_with_gpt4(desc_prompt)


def generate_alternative_description(description):
    prompt = f"""
    This is a product description for a garment by a company called Ripe. Please rewrite the description by simply adding in the term Ripe before the name of the garment in a grammatically appropriate manner.
    Ensure you write Ripe only once upon the first mention of the garment name. The rest of the product description should be left exactly the same.

    {description}
    """
    
    return chat_with_gpt4(prompt)

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

def process_row(row, style_descriptions, style_htmls, alt_style_descriptions, alt_style_htmls):
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
        alt_description = generate_alternative_description(description)
        alt_html = generate_html(row, alt_description)
        style_descriptions[style_code] = description
        style_htmls[style_code] = html
        alt_style_descriptions[style_code] = alt_description
        alt_style_htmls[style_code] = alt_html
        st.subheader(style_code + ' ' + product_name)
        st.write('---------------')
        st.write('Description')
        st.write('---------------')
        st.write(description)
        st.write(alt_description)
        st.write('---------------')
        st.write('HTML')
        st.write('---------------')
        st.code(html)
        st.code(alt_html)
    else:
        description = style_descriptions[style_code]
        html = style_htmls[style_code]
        alt_description = alt_style_descriptions[style_code]
        alt_html = alt_style_htmls[style_code]

    return description, html, alt_description, alt_html

def process_dataframe(df):
    descriptions = []
    htmls = []
    style_descriptions = {}
    style_htmls = {}
    alt_descriptions = []
    alt_htmls = []
    alt_style_descriptions = {}
    alt_style_htmls = {}

    for index, row in df.iterrows():
        description, html, alt_description, alt_html = process_row(row, style_descriptions, style_htmls, alt_style_descriptions, alt_style_htmls)
        descriptions.append(description)
        htmls.append(html)
        alt_descriptions.append(alt_description)
        alt_htmls.append(alt_html)

    return descriptions, htmls, alt_descriptions, alt_htmls

if uploaded_file is not None:
    workbook = pd.ExcelFile(uploaded_file)

    with st.form(key='form_select'):
        sheet_name = st.selectbox("Select a sheet", workbook.sheet_names)
        submit_button = st.form_submit_button(label='Do it :)')

    if submit_button:
        df = pd.read_excel(workbook, sheet_name=sheet_name, na_filter=False)
        descriptions, htmls, alt_descriptions, alt_htmls = process_dataframe(df)

        data = {'Generated Descriptions': descriptions, 'Generated HTMLs': htmls, 'Alternative Descriptions': alt_descriptions, 'Alternative HTMLs': alt_htmls}
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


 
