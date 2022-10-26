from django.conf import settings
from twilio.rest import Client
import random
import os
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

class MessageHandler:

    phone = None
    otp = None

    def __init__(self, phone, otp):

        self.phone = phone
        self.otp = otp

    def send_otp_to_phone(self):
        account_sid = os.environ['ACCOUNT_SID']
        auth_token = os.environ['AUTH_TOKEN']
        client = Client(account_sid, auth_token)

        message = client.messages.create(
                                    body=f'Your OTP is {self.otp}',
                                    from_='+13464881972',
                                    to=self.phone
                                )

    

    