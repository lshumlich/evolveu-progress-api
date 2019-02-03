
# import pytest
import os


# from google.oauth2 import id_token
# from google.auth.transport import requests

# print("Hello World")
# print(id_token)

print(os.environ)

import os
try:
    user_paths = os.environ['PYTHONPATH'].split(os.pathsep)
except KeyError:
    user_paths = []