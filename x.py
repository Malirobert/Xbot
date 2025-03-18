from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import random
import os

class XBot:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        
        # Créer le dossier chrome_profile s'il n'existe pas
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.profile_path = os.path.join(current_dir, 'chrome_profile')
        if not os.path.exists(self.profile_path):
            os.makedirs(self.profile_path)
            
        # Configuration de Chrome avec le profil persistant
        options = webdriver.ChromeOptions()
        options.add_argument(f'--user-data-dir={self.profile_path}')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        self.driver = webdriver.Chrome(options=options)

    def is_logged_in(self):
        """Vérifie si l'utilisateur est déjà connecté"""
        try:
            self.driver.get("https://x.com/messages")
            time.sleep(3)
            
            # Vérifier si on est sur la page de connexion
            if "login" in self.driver.current_url:
                print("Pas de session active trouvée, connexion nécessaire")
                return False
                
            # Vérifier si on peut accéder aux messages
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='NewDM_Button']"))
                )
                print("Session active trouvée! Utilisation de la session existante")
                return True
            except:
                return False
                
        except Exception as e:
            print(f"Erreur lors de la vérification de la session: {str(e)}")
            return False

    def perform_login(self):
        """Effectue le processus de connexion complet"""
        try:
            print("Démarrage du processus de connexion...")
            self.driver.get("https://x.com/i/flow/login")
            time.sleep(random.uniform(2, 3))
            
            # Entrer le nom d'utilisateur
            print("Saisie du nom d'utilisateur...")
            username_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "text"))
            )
            self.human_typing(username_input, self.username)
            time.sleep(random.uniform(0.8, 1.5))
            username_input.send_keys(Keys.RETURN)
            
            # Entrer le mot de passe
            print("Saisie du mot de passe...")
            time.sleep(random.uniform(1.5, 2.5))
            password_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            self.human_typing(password_input, self.password)
            time.sleep(random.uniform(0.8, 1.5))
            password_input.send_keys(Keys.RETURN)
            
            # Attendre que la connexion soit établie
            time.sleep(random.uniform(3, 4))
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de la connexion: {str(e)}")
            return False

    def login(self):
        """Gère la connexion avec vérification de session"""
        try:
            # Vérifier d'abord si on est déjà connecté
            if self.is_logged_in():
                return True
            
            # Si non connecté, effectuer le processus de connexion
            print("Tentative de connexion...")
            if self.perform_login():
                # Vérifier si la connexion a réussi
                return self.is_logged_in()
            return False
            
        except Exception as e:
            print(f"Erreur lors du processus de connexion: {str(e)}")
            return False

    def human_typing(self, element, text):
        """Simule une saisie humaine"""
        for char in text:
            time.sleep(random.uniform(0.1, 0.4))
            element.send_keys(char)
            if random.random() < 0.1:
                time.sleep(random.uniform(0.5, 1.0))
        time.sleep(random.uniform(0.5, 1.2))

    def send_dm(self, recipient, message):
        try:
            print(f"Début de l'envoi à {recipient}...")
            
            # Vérifier si toujours connecté avant d'envoyer
            if not self.is_logged_in():
                print("Session expirée, tentative de reconnexion...")
                if not self.login():
                    raise Exception("Impossible de restaurer la session")
            
            print("1. Navigation vers la page des messages...")
            self.driver.get("https://x.com/messages")
            time.sleep(random.uniform(2, 3))
            
            print("2. Clic sur 'New message'...")
            new_message_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='NewDM_Button'], [aria-label='New message']"))
            )
            new_message_button.click()
            time.sleep(random.uniform(1, 2))
            
            print(f"3. Recherche de l'utilisateur {recipient}...")
            search_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='searchPeople']"))
            )
            self.human_typing(search_input, recipient)
            time.sleep(random.uniform(1.5, 2.5))
            
            print("4. Sélection du premier résultat...")
            first_result = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='TypeaheadUser']"))
            )
            first_result.click()
            time.sleep(random.uniform(0.8, 1.5))
            
            print("5. Clic sur 'Next'...")
            next_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='nextButton']"))
            )
            next_button.click()
            time.sleep(random.uniform(1, 2))
            
            print("6. Saisie du message...")
            message_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='dmComposerTextInput']"))
            )
            self.human_typing(message_input, message)
            time.sleep(random.uniform(0.8, 1.5))
            
            print("7. Envoi du message...")
            send_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='dmComposerSendButton']"))
            )
            send_button.click()
            
            print(f"Message envoyé avec succès à {recipient}")
            time.sleep(random.uniform(2, 3))
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'envoi du DM à {recipient}: {str(e)}")
            return False

    def close(self):
        """Ferme le navigateur sans effacer les données"""
        try:
            self.driver.quit()
        except Exception as e:
            print(f"Erreur lors de la fermeture du navigateur: {str(e)}") 