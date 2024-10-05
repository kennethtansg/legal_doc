import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from dotenv import load_dotenv
import os  # Uncommented to access environment variables

def page_setup():
    st.header("Chat with your PDF!", anchor=False)

    hide_menu_style = """
            <style>
            #MainMenu {visibility: hidden;}
            .stDeployButton {display:none;}
            [data-testid="stToolbar"] {visibility: hidden !important;}
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_menu_style, unsafe_allow_html=True)

def get_llminfo():
    st.sidebar.header("Options")
    # tip1 = "Select a model you want to use."
    # model = st.sidebar.radio("Choose LLM:",
    #                          ("gemini-1.5-flash",
    #                           "gemini-1.5-pro"), help=tip1)
    model = "gemini-1.5-flash"
    tip2 = "Lower temperatures are good for prompts that require a less open-ended or creative response, while higher temperatures can lead to more diverse or creative results. A temperature of 0 means that the highest probability tokens are always selected."
    temp = st.sidebar.slider("Temperature:", min_value=0.0,
                             max_value=2.0, value=1.0, step=0.25, help=tip2)
    tip3 = "Used for nucleus sampling. Specify a lower value for less random responses and a higher value for more random responses."
    topp = st.sidebar.slider("Top P:", min_value=0.0,
                             max_value=1.0, value=0.94, step=0.01, help=tip3)
    tip4 = "Number of response tokens, 8194 is the limit."
    maxtokens = st.sidebar.slider("Maximum Tokens:", min_value=100,
                                  max_value=5000, value=2000, step=100, help=tip4)
    return model, temp, topp, maxtokens

def check_authentication():
    """Check if the user is authenticated."""
    if 'authenticated' not in st.session_state or not st.session_state['authenticated']:
        st.warning("Please log in to access this page.")
        st.stop()

def main():
    # check_authentication()  # Ensure the user is authenticated
    load_dotenv()  # Load environment variables from .env file

    # Retrieve the API key from environment variables
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        st.error("API key not found. Please set GOOGLE_API_KEY in the .env file.")
        st.stop()

    # Configure the Google Generative AI with the retrieved API key
    genai.configure(api_key=api_key)

    page_setup()
    model_name, temperature, top_p, max_tokens = get_llminfo()

    uploaded_file = st.file_uploader("Choose a PDF file", type='pdf', accept_multiple_files=False)
       
    if uploaded_file:
        text = ""
        pdf_reader = PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            extracted_text = page.extract_text()
            if extracted_text:  # Check if text extraction was successful
                text += extracted_text

        if not text:
            st.warning("No text could be extracted from the uploaded PDF.")
            st.stop()

        generation_config = {
            "temperature": temperature,
            "top_p": top_p,
            "max_output_tokens": max_tokens,
            "response_mime_type": "text/plain",
        }
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config
        )
        # st.write(f"Total tokens in the PDF: {model.count_tokens(text)}") 
        question = st.text_input("Enter your question and hit return.")
        if question:
            response = model.generate_content([question, text])
            st.write(response.text)

if __name__ == '__main__':
    main()
