import streamlit as st
import requests
import re

# Clean and sanitize header inputs to prevent Latin-1 encoding exceptions
def sanitize_header_value(value: str) -> str:
    if not value:
        return ""
    return re.sub(r'[^\x00-\xff]', '', value).strip()

st.set_page_config(
    page_title="Groq Document Extraction Agent",
    page_icon="📄",
    layout="centered"
)

st.title("📄 Groq Document Extraction Agent")
st.write("Upload a PDF document below to extract key bullet points instantly using your own free Groq Key.")
st.markdown("---")

st.sidebar.header("🔧 Settings & Authentication")

# MAKE SURE THIS MATCHES YOUR ACTIVE RENDER BACKEND API ADDRESS
raw_backend_url = st.sidebar.text_input(
    "Live Backend Endpoint URL", 
    value="https://document-agent-api.onrender.com/extract-points"
)

raw_api_key = st.sidebar.text_input(
    "Your Groq API Key", 
    type="password",
    placeholder="gsk_..."
)

uploaded_file = st.file_uploader("Upload a PDF file to analyze", type=["pdf"])

if uploaded_file is not None:
    BACKEND_URL = raw_backend_url.strip()
    USER_API_KEY = sanitize_header_value(raw_api_key)

    if not USER_API_KEY:
        st.error("🔑 Please enter a valid Groq API Key (starts with gsk_) in the sidebar!")
    else:
        with st.spinner("🤖 Agent is analyzing your document via Groq... Please wait."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                headers = {"X-Groq-API-Key": USER_API_KEY}
                
                response = requests.post(BACKEND_URL, files=files, headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    points = result.get("points", [])
                    
                    st.success("✅ Extraction Complete!")
                    st.subheader("📋 Key Points Extracted:")
                    for item in points:
                        st.markdown(item)
                else:
                    try:
                        error_msg = response.json().get('detail', 'Unknown backend error occurred.')
                    except ValueError:
                        error_msg = f"Backend returned status {response.status_code} (HTML). Please verify that your Live Backend Endpoint URL ends with '/extract-points' and has no typos!"
                    
                    st.error(f"❌ Error from Agent: {error_msg}")
                    
            except requests.exceptions.ConnectionError:
                st.error(f"❌ Connection Failed! Could not communicate with the API at: {BACKEND_URL}. Check if your backend service on Render is live or sleeping.")