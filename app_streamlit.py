import streamlit as st
from google import genai


st.title("Gemini Canvas Prompt")

prompt = st.text_area("Enter your prompt:")

if st.button("Submit"):
    if prompt:
        client = genai.Client(api_key="AIzaSyDn8qVqu6Sqhv-_agnP2A18JTPq-4Fp4AM")
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash", contents=prompt
            )
            st.subheader("Response:")
            st.write(response.text)
        except Exception as e:
            st.error(f"Error: {e}") 