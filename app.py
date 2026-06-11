import streamlit as st
import io
from pypdf import PdfReader
from groq import Groq
import re

# Clean and sanitize API key inputs to prevent character encoding issues
def sanitize_input(value: str) -> str:
    if not value:
        return ""
    return re.sub(r'[^\x00-\xff]', '', value).strip()

st.set_page_config(
    page_title="Groq Document Extraction Agent",
    page_icon="📄",
    layout="centered"
)

st.title("📄 Groq Document Extraction Agent")
st.write("Upload a PDF document below to extract key bullet points instantly using your own Groq Key.")
st.markdown("---")

# Sidebar for user authentication details
st.sidebar.header("🔧 Authentication")
raw_api_key = st.sidebar.text_input(
    "Your Groq API Key", 
    type="password",
    placeholder="gsk_..."
)

uploaded_file = st.file_uploader("Upload a PDF file to analyze", type=["pdf"])

if uploaded_file is not None:
    USER_API_KEY = sanitize_input(raw_api_key)

    if not USER_API_KEY:
        st.sidebar.error("🔑 Please enter your Groq API Key to begin!")
    else:
        with st.spinner("🤖 Extracting text and analyzing via Groq... Please wait."):
            try:
                # 1. Parse the PDF bytes directly in-memory
                pdf_file = io.BytesIO(uploaded_file.getvalue())
                reader = PdfReader(pdf_file)
                document_text = ""
                
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        document_text += text + "\n"
                
                if not document_text.strip():
                    st.error("❌ The uploaded PDF contains no extractable text.")
                else:
                    # 2. Initialize the Groq Client using the user's provided key
                    client = Groq(api_key=USER_API_KEY)
                    
                    prompt = (
                        "Extract all the key bullet points from this document text. "
                        "Format the output as a clean, easy-to-read Markdown numbered list "
                        "using '1. ', '2. ', '3. ' format."
                        f"\n\nDocument Text:\n{document_text}"
                    )

                    # 3. Stream data straight to Groq's fast inference engine
                    chat_completion = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama-3.3-70b-versatile"
                    )
                    
                    # 4. Display the response directly on the Streamlit dashboard
                    output_text = chat_completion.choices[0].message.content
                    st.success("✅ Extraction Complete!")
                    st.subheader("📋 Key Points Extracted:")
                    st.markdown(output_text)
                    
            except Exception as e:
                st.error(f"❌ Error during processing: {str(e)}")