# Force a reload of the .env file to update the environment variables
# 
# usage:
# from env_utils import reload_dotenv 
# reload_dotenv()
#
# required packages:
# pip install python-dotenv

import os
from dotenv import dotenv_values

def reload_dotenv():
    # Load the current environment variables
    # current_env_vars = dict(os.environ)
    # Load the .env file variables
    dotenv_vars = dotenv_values('.env')
    # Update the current environment variables with the .env file variables
    for key, value in dotenv_vars.items():
        os.environ[key] = value
        
reload_dotenv()

