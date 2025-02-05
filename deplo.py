

# main.py
import streamlit as st
import google.generativeai as genai
import base64

def main():
    # Set page config for wider layout
    st.set_page_config(layout="wide")
    
    # Custom CSS to adjust spacing and layout
    st.markdown("""
        <style>
        .stButton button {
            width: 100%;
            margin-top: 20px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("Coupang Project")
    st.write("Upload an image, and the Gemini API will extract the table data in JSON format.")

    # Initialize session state
    if 'extracted_json' not in st.session_state:
        st.session_state.extracted_json = None
    if 'translated_json' not in st.session_state:
        st.session_state.translated_json = None

    # Configure Gemini API with direct API key
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)

    # File uploader in a container
    upload_container = st.container()
    with upload_container:
        uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Create two columns for image and process button
        col1, col2 = st.columns([2, 1])
        with col1:
            st.image(uploaded_file, use_container_width=True)
        with col2:
            st.write("")  # Add some spacing
            st.write("")  # Add some spacing
            process_button = st.button("Process Image", use_container_width=True)

        if process_button or st.session_state.extracted_json is None:
            image_data = base64.b64encode(uploaded_file.read()).decode("utf-8")
            mime_type = uploaded_file.type
            model = genai.GenerativeModel("gemini-1.5-flash")

            example_json = """
            {
                [
                    {
                        "Size": "XS(085)", 
                        "어깨너비": "53.5",
                        "소매길이": "57.5",
                        "전체길이": "64",  
                        "가슴둘레": "123"  
                    }
                ]
            }
            """

            payload = [
                {"mime_type": mime_type, "data": image_data},
                {"text": f"Extract table from image and return in JSON format. Example format: {example_json}"}
            ]

            with st.spinner("Processing..."):
                response = model.generate_content(payload)
                st.session_state.extracted_json = response.text

        # Create three columns for the JSON display and translate button
        if st.session_state.extracted_json:
            col1, col2, col3 = st.columns([5, 2, 5])
            
            with col1:
                st.subheader("Original JSON")
                st.code(st.session_state.extracted_json, language="json")
            
            with col2:
                st.write("")  # Add some spacing
                st.write("")  # Add some spacing
                translate_button = st.button("Translate to English →", use_container_width=True)
            
            with col3:
                st.subheader("English Translation")
                if translate_button:
                    with st.spinner("Translating..."):
                        translation_model = genai.GenerativeModel("gemini-1.5-flash")
                        translation_response = translation_model.generate_content(
                            f"""Translate this JSON to English, maintaining the exact same JSON structure.
                            Convert all Korean keys and text to English. Return only the JSON, no additional text:
                            {st.session_state.extracted_json}"""
                        )
                        st.session_state.translated_json = translation_response.text
                
                if st.session_state.translated_json:
                    st.code(st.session_state.translated_json, language="json")

    else:
        st.info("Please upload an image file to begin.")

if __name__ == "__main__":
    main()