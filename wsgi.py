import sys
import os
from dotenv import load_dotenv

project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path = [project_home] + sys.path
os.chdir(project_home)
load_dotenv(os.path.join(project_home, '.env'))

# If using Flask/FastAPI, import the app object here. Otherwise, adjust as needed.
# from main import app as application

def application(environ, start_response):
    status = '200 OK'
    output = b'Health: OK'
    response_headers = [('Content-type', 'text/plain'), ('Content-Length', str(len(output)))]
    start_response(status, response_headers)
    return [output] 