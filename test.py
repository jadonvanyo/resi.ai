from cryptography.fernet import Fernet
from flask import session
from cs50 import SQL


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///resi.db")

# SELECT the user's encrypted API key from users
encrypted_api_key = (db.execute(
        "SELECT api_key FROM users WHERE id = ?;", 1
))[0]["api_key"]
print(encrypted_api_key)

def decrypt_key(encrypted_key, fernet_instance):
    """Decrypt a user's API key"""
    return fernet_instance.decrypt(encrypted_key).decode()

def get_fernet_instance():
    """Initialize and return a Fernet instance using a secret key"""
    # TODO: Create your own secret key and update the file path to the file with the secret key
    # Open the file containing the secret key
    with open('/Users/jadonvanyo/Desktop/cs50/final_project/secret_keys/secret_key.txt', 'r', encoding='utf-8') as file:
        # Generate fernet instance to encrypt the user's secret key from secret key in file
        fernet_instance = Fernet(file.read().strip())
    
    return fernet_instance

print(decrypt_key(encrypted_api_key, get_fernet_instance()))