import hashlib
import msvcrt
import sys
import random
import string

CHARSET = 'abcdefghijklmnopqrstuvwxyz0123456789'

def get_salt(length=8):
    """Generates a random alphanumeric salt."""
    salt_chars = string.ascii_lowercase + string.digits 
    return "".join(random.choice(salt_chars) for _ in range(length))

def get_masked_input(prompt):
    """Function for input with explicit asterisk display."""
    print(prompt, end='', flush=True)
    
    password = ""
    while True:
        char = msvcrt.getwch()
            
        if char == '\r':
            print()
            break
        elif char == '\b':
            if password:
                password = password[:-1]
                sys.stdout.write('\b \b')
                sys.stdout.flush()
        elif char == '\x03':
            raise KeyboardInterrupt
        else:
            password += char
            sys.stdout.write('*')
            sys.stdout.flush()
    
    return password

def get_pin():
    """Gets a pin from the user and validates it."""
    while True:
        try:
            pin = get_masked_input("Enter secret (lowercase a-z, 0-9 only): ")
        except KeyboardInterrupt:
            print("\nCancelled.")
            return None
        
        # Validate the pin
        valid = True
        if not pin:
            print("\nError: PIN cannot be empty.")
            continue
            
        for char in pin:
            if char not in CHARSET:
                print("\nError: Character '%s' is not in the allowed charset (a-z, 0-9)." % char)
                valid = False
                break
        
        if valid:
            return pin

secret_pin = get_pin()

if secret_pin:
    # 1. Generate the salt
    salt = get_salt(8)
    pin_length = len(secret_pin)
    
    # 2. Create the salted hash
    salted_pin = secret_pin + salt

    hash_object = hashlib.md5(salted_pin.encode('utf-8')) 
    hex_hash = hash_object.hexdigest()

    try:
        with open('input.txt', 'w') as f:
            f.write("%s\n" % hex_hash)   # Line 1: The hash
            f.write("%s\n" % salt)       # Line 2: The salt
            f.write("%d\n" % pin_length) # Line 3: The length
            
        print("-" * 30)
        print("Created 'input.txt' successfully.")
        print("Target Hash: %s" % hex_hash)
        print("Salt: %s" % salt)
        print("PIN Length: %d" % pin_length)

    except Exception as e:
        print("Error writing file: %s" % e)