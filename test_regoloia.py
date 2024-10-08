import streamlit as st
import requests
import json

# Page configuration
st.set_page_config(page_title="Mercato-GuidAI", page_icon=":robot_face:", layout="wide")

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
    message = "Ho bisogno di consigli sulla strategia di internazionalizzazione basata sulle seguenti informazioni:\n\n"
    for key, value in form_data.items():
        if value:  # Only include non-empty fields
            message += f"- {key.capitalize()}: {value}\n"
    message += """\nPer caso, nella tua base di conoscenza hai informazione per rispondere queste domande secondo la mia impresa e il mio settore:
                1. Quali mercati esteri potrebbero essere interessanti per la azienda? \n
                2. Quali sono le caratteristiche dei potenziali clienti in questi mercati? \n
                3. Quali sono le tendenze di mercato e le esigenze dei clienti in questi paesi?\n
                4. Quali sono le barriere all’ingresso e le sfide che potresti affrontare in questi mercati?\n
                5. Il prodotto/servizio è adatto al nuovo mercato o richiede modifiche?\n

                Dopo la tua risposta mi puoi chiedere di scegliere in che mercato mi voglio internazzionalizare?\n
                Cosí mi rispondi a posteriori anche queste domande secondo il mio mercato scelto:\n
                1. Chi sono i principali concorrenti nei mercati target per i mieri prodotti o servizi? \n
                2. Quali sono le loro strategie di marketing e vendita?\n
                3. Come posso  differenziarmi dalla concorrenza e offrire valore aggiunto ai clienti?"""
    return message

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Sei un assistente AI specializzato in strategie di internazionalizzazione. Fornisci consigli in base al contesto fornito."}
    ]
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False
if 'show_chat' not in st.session_state:
    st.session_state.show_chat = False
if 'embeddings' not in st.session_state:
    st.session_state.embeddings = None

# Sidebar for navigation
st.sidebar.image("Logo-Mercato-Guidai-letras.png", width=170)  # Display logo in sidebar
st.sidebar.title("Inizia il Tuo Percorso di Internazionalizzazione")
page = st.sidebar.radio("Go to", ["Mercato GuidAI", "Embeddings"])

# Embeddings page
if page == "Embeddings":
    st.title("Mercato-GuidAI Embeddings")
    
    url = st.text_input("Endpoint", "https://api.regolo.ai/v1/embeddings")
    token = st.text_input("Authorization Token", "rai_eecheeShuH5aiZuiphaiy7eLee5As0ai", type="password")
    
    # List of document files
    document_files = ["Doing_Export_Report_2024_SACE.txt", "Rapporto_Obiettivo_sparkling.txt"]
    
    # Read the content of the document files
    documents = []
    for file in document_files:
        with open(file, "r", encoding="utf-8") as f:
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
                with st.spinner("L'IA sta analizzando le tue informazioni..."):
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
                with st.spinner("L'IA sta analizzando le tue informazioni..."):
                    ai_response = get_ai_response("https://api.regolo.ai/v1/chat/completions", 
                                                  "rai_eecheeShuH5aiZuiphaiy7eLee5As0ai", 
                                                  st.session_state.messages)
                st.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})

        if prompt := st.chat_input("Fai una domanda di follow-up"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                with st.spinner("L'IA sta pensando..."):
                    full_response = get_ai_response("https://api.regolo.ai/v1/chat/completions", 
                                                    "rai_eecheeShuH5aiZuiphaiy7eLee5As0ai", 
                                                    st.session_state.messages)
                message_placeholder.markdown(full_response)
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Inizia nuova consulenza"):
            # Read content from a .txt file
            with open("prompt_mercatoai.txt", "r", encoding="utf-8") as file:
                file_content = file.read()
            
            # Add embeddings context to the system message
            if st.session_state.embeddings:
                file_content += "\n\nEmbeddings Context:\n"
                file_content += json.dumps(st.session_state.embeddings, indent=2)
            
            st.session_state.messages = [
                {"role": "system", "content": file_content}
            ]
            st.session_state.form_submitted = False
            st.session_state.show_chat = False
            st.rerun()



