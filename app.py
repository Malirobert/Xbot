import streamlit as st
import pandas as pd
from datetime import datetime
import time
from x import XBot
import threading
from database import MessageDatabase
import csv
import os

# Configuration de la page
st.set_page_config(
    page_title="X DM Bot",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Styles CSS personnalisés
st.markdown("""
    <style>
    .stApp {
        background-color: #000000;
    }
    .main {
        color: #FFFFFF;
    }
    .stButton>button {
        color: #FFFFFF;
        background-color: #2C3E50;
        border: 1px solid #FFFFFF;
    }
    .status-ready {
        color: #28a745;
    }
    .status-waiting {
        color: #dc3545;
    }
    /* Styles additionnels pour le thème sombre */
    .st-bw {
        color: #FFFFFF;
    }
    .st-eb {
        color: #FFFFFF;
    }
    /* Style pour les conteneurs */
    .stTextInput>div>div>input {
        color: #FFFFFF;
        background-color: #1E1E1E;
    }
    .stNumberInput>div>div>input {
        color: #FFFFFF;
        background-color: #1E1E1E;
    }
    /* Style pour les titres et sous-titres */
    h1, h2, h3 {
        color: #FFFFFF !important;
    }
    .stTextArea textarea {
        color: #FFFFFF;
        background-color: #1E1E1E;
    }
    .uploadedFile {
        color: #FFFFFF;
        background-color: #1E1E1E;
    }
    /* Style pour le texte de statut */
    p {
        color: #FFFFFF;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialisation des variables de session
def init_session_state():
    # Variables de base
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []
    if 'bot_running' not in st.session_state:
        st.session_state['bot_running'] = False
    if 'bot_paused' not in st.session_state:
        st.session_state['bot_paused'] = False
    if 'db' not in st.session_state:
        st.session_state['db'] = MessageDatabase()
    # Variables pour les champs de saisie
    if 'input_username' not in st.session_state:
        st.session_state['input_username'] = ""
    if 'input_password' not in st.session_state:
        st.session_state['input_password'] = ""
    if 'input_delay' not in st.session_state:
        st.session_state['input_delay'] = 1

# Appeler l'initialisation
init_session_state()

# Titre principal
st.title("X(Twitter) DM Bot")

# Section Configuration
with st.container():
    st.subheader("Configuration")
    
    # Champs de configuration
    username = st.text_input("Username:", key="username_widget")
    password = st.text_input("Password:", type="password", key="password_widget")
    delay = st.number_input("Delay (minutes):", min_value=1, value=1, key="delay_widget")
    
    uploaded_file = st.file_uploader("CSV File:", type=['csv'])

# Section Historique
with st.container():
    st.subheader("Message History")
    
    # Création d'un conteneur pour l'historique avec défilement
    history_container = st.empty()
    
    # Fonction pour mettre à jour l'historique
    def update_history():
        try:
            messages = []
            if hasattr(st.session_state, 'messages'):
                messages = st.session_state.messages
            history_text = "\n".join([f"[{msg['timestamp']}] {msg['username']}: {msg['status']}" 
                                    for msg in messages])
            history_container.text_area("Message History", 
                                      value=history_text,
                                      height=200,
                                      disabled=True)
        except Exception as e:
            print(f"Error updating history: {str(e)}")

# Section Contrôle
with st.container():
    col1, col2, col3 = st.columns(3)
    
    def start_bot():
        if not st.session_state.bot_running:
            # Vérification des entrées
            if not username or not password or not uploaded_file:
                st.error("Please fill all required fields")
                return
            
            try:
                # Lire et valider le CSV
                df = pd.read_csv(uploaded_file)
                if 'username' not in df.columns or 'message' not in df.columns:
                    st.error("CSV file must contain 'username' and 'message' columns")
                    return
                
                # Convertir le DataFrame en liste de dictionnaires
                messages_list = df.to_dict('records')
                
                # Stocker les données dans une variable globale
                global bot_config
                bot_config = {
                    'username': username,
                    'password': password,
                    'delay': delay,
                    'messages': messages_list,
                    'is_running': True,
                    'is_paused': False
                }
                
                st.session_state.bot_running = True
                st.session_state.bot_paused = False
                
                # Démarrer le thread
                bot_thread = threading.Thread(target=run_bot, daemon=True)
                bot_thread.start()
                
            except Exception as e:
                st.error(f"Error starting bot: {str(e)}")

    def pause_bot():
        bot_config['is_paused'] = not bot_config['is_paused']
        st.session_state.bot_paused = bot_config['is_paused']

    def stop_bot():
        bot_config['is_running'] = False
        bot_config['is_paused'] = False
        st.session_state.bot_running = False
        st.session_state.bot_paused = False

    with col1:
        start_button = st.button("Start Bot", 
                               disabled=st.session_state.bot_running,
                               on_click=start_bot)
    with col2:
        pause_button = st.button("Pause Bot", 
                               disabled=not st.session_state.bot_running,
                               on_click=pause_bot)
    with col3:
        stop_button = st.button("Stop Bot", 
                              disabled=not st.session_state.bot_running,
                              on_click=stop_bot)

# Affichage du statut
status_text = "Running" if st.session_state.bot_running else "Waiting for input"
status_color = "status-ready" if st.session_state.bot_running else "status-waiting"
st.markdown(f"<p class='{status_color}'>Status: {status_text}</p>", unsafe_allow_html=True)

def add_to_history(username, status):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-4]
        new_message = {
            "timestamp": timestamp,
            "username": username,
            "status": status
        }
        
        if 'messages' not in st.session_state:
            st.session_state.messages = []
            
        st.session_state.messages.append(new_message)
        st.session_state.db.add_message(username, status)
        update_history()
    except Exception as e:
        print(f"Error in add_to_history: {str(e)}")

def run_bot():
    try:
        # Utiliser les variables du bot_config
        local_username = bot_config['username']
        local_password = bot_config['password']
        local_delay = bot_config['delay']
        messages = bot_config['messages']
        
        bot = XBot(local_username, local_password)
        
        if not bot.login():
            print("Login failed")
            add_to_history("System", "Login failed")
            return
            
        print("Bot logged in successfully")
        add_to_history("System", "Bot started")
        
        for message_data in messages:
            if not bot_config['is_running']:
                break
                
            while bot_config['is_paused']:
                time.sleep(1)
                if not bot_config['is_running']:
                    break
            
            try:
                target_username = message_data['username']
                message = message_data['message']
                
                print(f"Sending message to {target_username}")
                success = bot.send_dm(target_username, message)
                
                status = "sent" if success else "failed"
                add_to_history(target_username, status)
                
                if success:
                    print(f"Message sent to {target_username}")
                else:
                    print(f"Failed to send message to {target_username}")
                
                time.sleep(local_delay * 60)
                
            except Exception as e:
                error_msg = f"Error sending message to {target_username}: {str(e)}"
                print(error_msg)
                add_to_history(target_username, f"error: {str(e)}")
                continue
                
        bot.close()
        add_to_history("System", "Bot finished")
        
    except Exception as e:
        error_msg = f"Bot error: {str(e)}"
        print(error_msg)
        add_to_history("System", error_msg)
    finally:
        bot_config['is_running'] = False
        st.session_state.bot_running = False

# Footer
st.markdown("<p style='text-align: center; color: gray;'>Powered by EcomLeads</p>", 
           unsafe_allow_html=True)

# Mise à jour initiale de l'historique
update_history()

# Ajoutez cette fonction pour la validation des entrées
def validate_inputs():
    if not username:
        return False, "Username is required"
    if not password:
        return False, "Password is required"
    if not uploaded_file:
        return False, "CSV file is required"
    return True, ""

# Ajoutez au début du fichier, après les imports
bot_config = {} 