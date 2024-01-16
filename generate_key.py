from cryptography.fernet import Fernet

# Generate a key (Do this once and store the key in a local file: secret_key.txt)
# Save this key somewhere safe
secret_key = Fernet.generate_key()

# Print the secret key to the terminal
print(secret_key)