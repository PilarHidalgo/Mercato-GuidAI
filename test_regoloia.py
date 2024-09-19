import streamlit as st
import requests
import json

# Page configuration
st.set_page_config(page_title="Consult REGOLOAI Documents", page_icon=":robot_face:", layout="wide")

# Custom CSS with updated colors
st.markdown("""
<style>
    .stApp {
        background-color: #0d2244; /* Dark blue background */
    }
    .css-1d391kg {
        background-color: #0d2244; /* Dark blue background for main content */
    }
    .stButton>button {
        background-color: #ea463c; /* Red button color */
        color: white;
    }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #1e3a5f; /* Light blue for inputs */
        color: white;
    }
    h1, h2, h3 {
        color: #049272; /* Green color for titles */
    }
    .stRadio>div {
        background-color: #1e3a5f; /* Light blue for radio buttons */
        padding: 10px;
        border-radius: 5px;
    }
    .stChat {
        background-color: #1e3a5f; /* Light blue for chat background */
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .logo {
        display: block;
        margin: auto;
        width: 100px; /* Adjust width as needed */
        padding-bottom: 20px;
    }
    .stSidebar .stImage {
        margin-bottom: 20px;
    }
    /* Additional selectors to ensure all grey areas are covered */
    .stSelectbox, .stMultiSelect {
        background-color: #1e3a5f;
        color: white;
    }
    .stDateInput>div>div>input {
        background-color: #1e3a5f;
        color: white;
    }
    .stSlider>div>div>div {
        background-color: #1e3a5f;
    }
</style>
""", unsafe_allow_html=True)

# Function to get embeddings
def get_embeddings(url, token, documents):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    data = {
        "model": "Alibaba-NLP/gte-Qwen2-7B-instruct",
        "input": documents
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# Function to get AI chat response
def get_ai_response(url, token, messages):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    data = {
        "model": "llama3.1:70b-instruct-q8_0",
        "messages": messages
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP Error: {e}")
        st.error(f"Response content: {response.text}")
        return f"Error: {str(e)}"
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return f"Error: {str(e)}"

# Function to process form data and create a structured message
def create_initial_message(form_data):
    message = "I need advice on internationalization strategy based on the following information:\n\n"
    for key, value in form_data.items():
        if value:  # Only include non-empty fields
            message += f"- {key.capitalize()}: {value}\n"
    message += "\nPlease provide an initial analysis and recommendations for internationalization based on this information."
    return message

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are an AI assistant specialized in internationalization strategies. Provide advice based on the given context."}
    ]
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False
if 'show_chat' not in st.session_state:
    st.session_state.show_chat = False

# Sidebar for navigation
st.sidebar.image("Logo-Mercato-Guidai-letras.png", width=170)  # Display logo in sidebar
st.sidebar.title("Inizia il Tuo Percorso di Internazionalizzazione")
page = st.sidebar.radio("Go to", ["Mercato GuidAI", "Embeddings"])

# Embeddings page
if page == "Embeddings":
    st.title("REGOLOAI Embeddings Interface")
    
    url = st.text_input("Endpoint", "https://api.regolo.ai/v1/embeddings")
    token = st.text_input("Authorization Token", "rai_eecheeShuH5aiZuiphaiy7eLee5As0ai", type="password")
    
    # List of document files
    document_files = ["documento1.txt", "documento2.txt"]
    
    # Read the content of the document files
    documents = []
    for file in document_files:
        with open(file, "r") as f:
            documents.append(f.read())
    
    if st.button("Get Embeddings"):
        with st.spinner('Calculating embeddings...'):
            embeddings = get_embeddings(url, token, documents)
            st.session_state.embeddings = embeddings
            st.write(embeddings)

# Chat AI page
elif page == "Mercato GuidAI":
    st.title("Mercato GuidAI")

    # If form hasn't been submitted, show the form
    if not st.session_state.form_submitted:
        with st.form("internationalization_form"):
            sector = st.text_input("Qual è il tuo settore di attività?")
            products = st.text_input("Quali sono i tuoi prodotti o servizi principali che vuoi internazionalizzare?")
           
            submit_button = st.form_submit_button("Invia e Scopri le Opportunità")

            if submit_button:
                form_data = {
                    "sector": sector,
                    "products": products
                }
                initial_message = create_initial_message(form_data)
                st.session_state.messages.append({"role": "user", "content": initial_message})
                
                # Get AI response immediately after form submission
                with st.spinner('AI is analyzing your information...'):
                    ai_response = get_ai_response("https://api.regolo.ai/v1/chat/completions", 
                                                  "rai_eecheeShuH5aiZuiphaiy7eLee5As0ai", 
                                                  st.session_state.messages)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                
                st.session_state.form_submitted = True
                st.session_state.show_chat = True
                st.rerun()

    # Chat interface
    if st.session_state.show_chat:
        st.markdown("<div class='stChat'>", unsafe_allow_html=True)
        for message in st.session_state.messages[1:]:  # Skip the system message
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if len(st.session_state.messages) % 2 == 1:  # If the last message is from the user
            with st.chat_message("assistant"):
                with st.spinner('AI is analyzing your information...'):
                    ai_response = get_ai_response("https://api.regolo.ai/v1/chat/completions", 
                                                  "rai_eecheeShuH5aiZuiphaiy7eLee5As0ai", 
                                                  st.session_state.messages)
                st.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})

        if prompt := st.chat_input("Ask a follow-up question"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                with st.spinner('AI is thinking...'):
                    full_response = get_ai_response("https://api.regolo.ai/v1/chat/completions", 
                                                    "rai_eecheeShuH5aiZuiphaiy7eLee5As0ai", 
                                                    st.session_state.messages)
                message_placeholder.markdown(full_response)
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Start New Consultation"):
            # Read content from a .txt file
            with open("path/to/your/file.txt", "r") as file:
                file_content = file.read()
            
            st.session_state.messages = [
                {"role": "system", "content": file_content}
            ]
            st.session_state.form_submitted = False
            st.session_state.show_chat = False
            st.rerun()
