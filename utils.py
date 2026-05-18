import secrets
import string
import threading
import os

from dotenv import load_dotenv

from flask import json
import requests



BREVO_URL= "https://api.brevo.com/v3/smtp/email"



def generate_random_otp(lenght: int):
    """Generate random number"""
    random_digits = [secrets.choice(string.digits) for _ in range(lenght)]
    return "".join(random_digits)

def send_registration_mail(
    to:str,
    user:str,
    otp:str,
    html_content:str
    ):
    payload = {  
            "sender":{  
                "name":"Flask App",
                "email":"gemmy1866@gmail.com"
            },
            "to":[  
            {  
                "email":user.email,
                "name":user.username
            }
            ],
                "subject":f"Verifiy Account: Your OTP is {otp}",
                "htmlContent": html_content
            }
    response = requests.post(
            url=BREVO_URL,
            headers={
                'accept': "application/json",
                'content-type':"application/json",
                'api-key':os.getenv("BREVO_API_KEY")
            },
            data=json.dumps(payload)
        )
    print(response.json())
    return response
    

