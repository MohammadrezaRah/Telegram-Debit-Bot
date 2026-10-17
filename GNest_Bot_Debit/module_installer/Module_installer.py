import subprocess
import sys
import os

os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)


# subprocess.check_call([sys.executable, "pip", "install", "-r", "requirements.txt"])

subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])

subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "jdatetime"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "aiogram"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "dotenv"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
subprocess.check_call([sys.executable, "-m", "playwright", "install"])







