import os
from dotenv import load_dotenv

def getKey():
    load_dotenv()
    return str(os.getenv('KEY'))
