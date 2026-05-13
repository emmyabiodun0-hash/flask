import secrets
import string
import threading

def generate_random_otp(lenght: int):
    """Generate random number"""
    random_digits = [secrets.choice(string.digits) for _ in range(lenght)]
    return "".join(random_digits)

