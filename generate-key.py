# Description: Generate MongoDB key.
# Result: Print out the generated key.
# Usage: python ./script.py

import os
import base64

def generate_mongodb_key():
    """
    Generate a MongoDB key.

    Returns:
        str: The base64-encoded key.
    """
    # Generate 756 random bytes
    secret = os.urandom(756)
    # Convert to a base64-encoded string
    return base64.b64encode(secret).decode('utf-8')

if __name__ == "__main__":
    print("MONGO DB KEY:", generate_mongodb_key())