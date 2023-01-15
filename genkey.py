# Generate new secret key for .env file
# Usage: python genkey.py

import os

print("Generating new secret key for .env file")
print('SECRET_KEY=' + os.urandom(48).hex())


