import hmac
import hashlib
import requests
import threading
import string
import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import json
# नोट: सुनिश्चित करें कि protobuf_decoder फोल्डर आपकी फाइल के साथ मौजूद है
try:
    from protobuf_decoder.protobuf_decoder import Parser
except ImportError:
    print("Error: protobuf_decoder library not found. Make sure the folder exists.")
    sys.exit()
import codecs
import time
from datetime import datetime
from colorama import Fore, Style, init
import urllib3
import os
import sys
import base64

# Initialize Colorama
init(autoreset=True)


# Disable only the InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

red = Fore.RED
lg = Fore.LIGHTGREEN_EX
green = Fore.GREEN
bold = Style.BRIGHT
purpel = Fore.MAGENTA
hex_key = "32656534343831396539623435393838343531343130363762323831363231383734643064356437616639643866376530306331653534373135623764316533"
key = bytes.fromhex(hex_key)

REGION_LANG = {"ME": "ar","IND": "hi","ID": "id","VN": "vi","TH": "th","BD": "bn","PK": "ur","TW": "zh","EU": "en","CIS": "ru","NA": "en","SAC": "es","BR": "pt"}
REGION_URLS = {"IND": "https://client.ind.freefiremobile.com/","ID": "https://clientbp.ggblueshark.com/","BR": "https://client.us.freefiremobile.com/","ME": "https://clientbp.common.ggbluefox.com/","VN": "https://clientbp.ggblueshark.com/","TH": "https://clientbp.common.ggbluefox.com/","CIS": "https://clientbp.ggblueshark.com/","BD": "https://clientbp.ggblueshark.com/","PK": "https://clientbp.ggblueshark.com/","SG": "https://clientbp.ggblueshark.com/","NA": "https://client.us.freefiremobile.com/","SAC": "https://client.us.freefiremobile.com/","EU": "https://clientbp.ggblueshark.com/","TW": "https://clientbp.ggblueshark.com/"}


def get_region(language_code: str) -> str:
    return REGION_LANG.get(language_code)

def get_region_url(region_code: str) -> str:
    return REGION_URLS.get(region_code, None)

def EnC_Vr(N):
    if N < 0: ''
    H = []
    while True:
        BesTo = N & 0x7F ; N >>= 7
        if N: BesTo |= 0x80
        H.append(BesTo)
        if not N: break
    return bytes(H)
    
def DEc_Uid(H):
    n = s = 0
    for b in bytes.fromhex(H):
        n |= (b & 0x7F) << s
        if not b & 0x80: break
        s += 7
    return n
    
def CrEaTe_VarianT(field_number, value):
    field_header = (field_number << 3) | 0
    return EnC_Vr(field_header) + EnC_Vr(value)

def CrEaTe_LenGTh(field_number, value):
    field_header = (field_number << 3) | 2
    encoded_value = value.encode() if isinstance(value, str) else value
    return EnC_Vr(field_header) + EnC_Vr(len(encoded_value)) + encoded_value

def CrEaTe_ProTo(fields):
    packet = bytearray()    
    for field, value in fields.items():
        if isinstance(value, dict):
            nested_packet = CrEaTe_ProTo(value)
            packet.extend(CrEaTe_LenGTh(field, nested_packet))
        elif isinstance(value, int):
            packet.extend(CrEaTe_VarianT(field, value))           
        elif isinstance(value, str) or isinstance(value, bytes):
            packet.extend(CrEaTe_LenGTh(field, value))           
    return packet


def E_AEs(Pc):
    Z = bytes.fromhex(Pc)
    key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    K = AES.new(key , AES.MODE_CBC , iv)
    R = K.encrypt(pad(Z , AES.block_size))
    return bytes.fromhex(R.hex())


def generate_random_name():
    super_digits = '⁰¹²³⁴⁵⁶⁷⁸⁹'
    name = 'NAJMI' + ''.join(random.choice(super_digits) for _ in range(5))
    return name

def generate_custom_password(random_length=9):
    characters = string.ascii_letters + string.digits
    random_part = ''.join(random.choice(characters) for _ in range(random_length)).upper()
    return F"NAJMI_FF_EXPERIMENT{random_part}"




GREEN = "\033[32m"
LIGHT_CYAN = "\033[96m"
LIGHT_YELLOW = "\033[93m"
LIGHT_GREEN = "\033[92m"
NEON_PURPLE = "\033[95m"
LIGHT_RED = "\033[91m"
LIGHT_MAGENTA = "\033[95m"
BRIGHT = "\033[1m"
RESET = "\033[0m"    

def create_acc(region):
    password = generate_custom_password()
    data = f"password={password}&client_type=2&source=2&app_id=100067"
    message = data.encode('utf-8')
    signature = hmac.new(key, message, hashlib.sha256).hexdigest()

    url = "https://100067.connect.garena.com/oauth/guest/register"

    headers = {
        "User-Agent": "GarenaMSDK/4.0.19P8(ASUS_Z01QD ;Android 12;en;US;)",
        "Authorization": "Signature " + signature,
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip",
        "Connection": "Keep-Alive"
    }

    try:
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            uid = response.json().get('uid')
            if uid:
                # print(f"{green}UID Created: {uid}{bold}")
                return token(uid, password, region)
    except Exception as e:
        pass
    # Retry if failed
    # return create_acc(region) 
    # Removed recursive retry to prevent stack overflow, handled in loop instead


def token(uid , password , region):
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"

    headers = {
        "Accept-Encoding": "gzip",
        "Connection": "Keep-Alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "100067.connect.garena.com",
        "User-Agent": "GarenaMSDK/4.0.19P8(ASUS_Z01QD ;Android 12;en;US;)",
    }

    body = {
        "uid": uid,
        "password": password,
        "response_type": "token",
        "client_type": "2",
        "client_secret": key,
        "client_id": "100067"
    }

    try:
        response = requests.post(url, headers=headers, data=body)
        open_id = response.json()['open_id']
        access_token = response.json()["access_token"]
        
        result = encode_string(open_id)
        field = to_unicode_escaped(result['field_14'])
        field = codecs.decode(field, 'unicode_escape').encode('latin1')
        # print(f"{purpel}Token Generated...{bold}")
        return Major_Regsiter(access_token , open_id , field, uid, password, region)
    except:
        return None

def encode_string(original):
    keystream = [
    0x30, 0x30, 0x30, 0x32, 0x30, 0x31, 0x37, 0x30,
    0x30, 0x30, 0x30, 0x30, 0x32, 0x30, 0x31, 0x37,
    0x30, 0x30, 0x30, 0x30, 0x30, 0x32, 0x30, 0x31,
    0x37, 0x30, 0x30, 0x30, 0x30, 0x30, 0x32, 0x30
    ]
    encoded = ""
    for i in range(len(original)):
        orig_byte = ord(original[i])
        key_byte = keystream[i % len(keystream)]
        result_byte = orig_byte ^ key_byte
        encoded += chr(result_byte)
    return {
        "open_id": original,
        "field_14": encoded
        }

def to_unicode_escaped(s):
    return ''.join(c if 32 <= ord(c) <= 126 else f'\\u{ord(c):04x}' for c in s)

def Major_Regsiter(access_token , open_id , field , uid , password, region):
    url = "https://loginbp.ggblueshark.com/MajorRegister"
    name = generate_random_name()

    headers = {
        "Accept-Encoding": "gzip",
        "Authorization": "Bearer",   
        "Connection": "Keep-Alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Expect": "100-continue",
        "Host": "loginbp.ggblueshark.com",
        "ReleaseVersion": "OB53",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_I005DA Build/PI)",
        "X-GA": "v1 1",
        "X-Unity-Version": "2018.4."
    }

    payload = {
        1: name,
        2: access_token,
        3: open_id,
        5: 102000007,
        6: 4,
        7: 1,
        13: 1,
        14: field,
        15: "en",
        16: 1,
        17: 1
    }

    payload = CrEaTe_ProTo(payload).hex()
    payload = E_AEs(payload).hex()
    body = bytes.fromhex(payload)

    try:
        response = requests.post(url, headers=headers, data=body, verify=False)
        return login(uid , password, access_token , open_id , response.content.hex() , response.status_code , name , region)
    except:
        return None

def encrypt_api(plain_text):
    plain_text = bytes.fromhex(plain_text)
    key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    cipher_text = cipher.encrypt(pad(plain_text, AES.block_size))
    return cipher_text.hex()


def chooseregion(data_bytes, jwt_token):
    url = "https://loginbp.ggblueshark.com/ChooseRegion"
    payload = data_bytes
    headers = {
        'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 12; M2101K7AG Build/SKQ1.210908.001)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/x-www-form-urlencoded",
        'Expect': "100-continue",
        'Authorization': f"Bearer {jwt_token}",
        'X-Unity-Version': "2018.4.11f1",
        'X-GA': "v1 1",
        'ReleaseVersion': "OB53"
    }
    try:
        response = requests.post(url, data=payload, headers=headers, verify=False)
        return response.status_code
    except:
        return 0


def login(uid , password, access_token , open_id, response , status_code , name , region):
    lang = get_region(region)
    if not lang: lang = "en"
    lang_b = lang.encode("ascii")
    headers = {
        "Accept-Encoding": "gzip",
        "Authorization": "Bearer",
        "Connection": "Keep-Alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Expect": "100-continue",
        "Host": "loginbp.ggblueshark.com",
        "ReleaseVersion": "OB53",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_I005DA Build/PI)",
        "X-GA": "v1 1",
        "X-Unity-Version": "2018.4.11f1"
    }    

    # Correct Payload for OB53 Login
    payload = b'\x1a\x132025-08-30 05:19:21"\tfree fire(\x01:\x081.114.13B2Android OS 9 / API-28 (PI/rel.cjw.20220518.114133)J\x08HandheldR\nATM MobilsZ\x04WIFI`\xb6\nh\xee\x05r\x03300z\x1fARMv7 VFPv3 NEON VMH | 2400 | 2\x80\x01\xc9\x0f\x8a\x01\x0fAdreno (TM) 640\x92\x01\rOpenGL ES 3.2\x9a\x01+Google|dfa4ab4b-9dc4-454e-8065-e70c733fa53f\xa2\x01\x0e105.235.139.91\xaa\x01\x02'+lang_b+b'\xb2\x01 1d8ec0240ede109973f3321b9354b44d\xba\x01\x014\xc2\x01\x08Handheld\xca\x01\x10Asus ASUS_I005DA\xea\x01@afcfbf13334be42036e4f742c80b956344bed760ac91b3aff9b607a610ab4390\xf0\x01\x01\xca\x02\nATM Mobils\xd2\x02\x04WIFI\xca\x03 7428b253defc164018c604a1ebbfebdf\xe0\x03\xa8\x81\x02\xe8\x03\xf6\xe5\x01\xf0\x03\xaf\x13\xf8\x03\x84\x07\x80\x04\xe7\xf0\x01\x88\x04\xa8\x81\x02\x90\x04\xe7\xf0\x01\x98\x04\xa8\x81\x02\xc8\x04\x01\xd2\x04=/data/app/com.dts.freefireth-PdeDnOilCSFn37p1AH_FLg==/lib/arm\xe0\x04\x01\xea\x04_2087f61c19f57f2af4e7feff0b24d9d9|/data/app/com.dts.freefireth-PdeDnOilCSFn37p1AH_FLg==/base.apk\xf0\x04\x03\xf8\x04\x01\x8a\x05\x0232\x9a\x05\n2019118692\xb2\x05\tOpenGLES2\xb8\x05\xff\x7f\xc0\x05\x04\xe0\x05\xf3F\xea\x05\x07android\xf2\x05pKqsHT5ZLWrYljNb5Vqh//yFRlaPHSO9NWSQsVvOmdhEEn7W+VHNUK+Q+fduA3ptNrGB0Ll0LRz3WW0jOwesLj6aiU7sZ40p8BfUE/FI/jzSTwRe2\xf8\x05\xfb\xe4\x06\x88\x06\x01\x90\x06\x01\x9a\x06\x014\xa2\x06\x014\xb2\x06"GQ@O\x00\x0e^\x00D\x06UA\x0ePM\r\x13hZ\x07T\x06\x0cm\\V\x0ejYV;\x0bU5'
    data = payload
    data = data.replace('afcfbf13334be42036e4f742c80b956344bed760ac91b3aff9b607a610ab4390'.encode(),access_token.encode())
    data = data.replace('1d8ec0240ede109973f3321b9354b44d'.encode(),open_id.encode())
    d = encrypt_api(data.hex())
    
    Final_Payload = bytes.fromhex(d)

    URL = "https://loginbp.ggblueshark.com/MajorLogin"
    try:
        RESPONSE = requests.post(URL, headers=headers, data=Final_Payload, verify=False) 
    
        if RESPONSE.status_code == 200:
            if len(RESPONSE.text) < 10:
                return False
            
            # Checking if region selection is needed
            if lang.lower() not in ["ar", "en"]:
                json_result = get_available_room(RESPONSE.content.hex())
                parsed_data = json.loads(json_result)
                try:
                    BASE64_TOKEN = parsed_data['8']['data']
                except:
                    return None

                # FORCE REGION from Argument
                fields = {1: region}
                fields = bytes.fromhex(encrypt_api(CrEaTe_ProTo(fields).hex()))
                r = chooseregion(fields, BASE64_TOKEN)

                if r == 200:
                    return login_server(uid , password, access_token , open_id, response , status_code , name , region)
            else:
                BASE64_TOKEN = RESPONSE.text[RESPONSE.text.find("eyJhbGciOiJIUzI1NiIsInN2ciI6IjEiLCJ0eXAiOiJKV1QifQ"):-1]
            
            second_dot_index = BASE64_TOKEN.find(".", BASE64_TOKEN.find(".") + 1)     
            BASE64_TOKEN = BASE64_TOKEN[:second_dot_index+44]
            dat = GET_PAYLOAD_BY_DATA(BASE64_TOKEN, access_token, 1, response, status_code, name, uid, password, region)
            return dat
    except Exception as e:
        return None
    

def login_server(uid , password, access_token , open_id, response , status_code , name , region):
    lang = get_region(region)
    lang_b = lang.encode("ascii")

    headers = {
        "Accept-Encoding": "gzip",
        "Authorization": "Bearer",
        "Connection": "Keep-Alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Expect": "100-continue",
        "Host": "loginbp.ggblueshark.com",
        "ReleaseVersion": "OB53",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_I005DA Build/PI)",
        "X-GA": "v1 1",
        "X-Unity-Version": "2018.4.11f1"
    }    

    # Login Server Payload
    payload = b'\x1a\x132025-08-30 05:19:21"\tfree fire(\x01:\x081.114.13B2Android OS 9 / API-28 (PI/rel.cjw.20220518.114133)J\x08HandheldR\nATM MobilsZ\x04WIFI`\xb6\nh\xee\x05r\x03300z\x1fARMv7 VFPv3 NEON VMH | 2400 | 2\x80\x01\xc9\x0f\x8a\x01\x0fAdreno (TM) 640\x92\x01\rOpenGL ES 3.2\x9a\x01+Google|dfa4ab4b-9dc4-454e-8065-e70c733fa53f\xa2\x01\x0e105.235.139.91\xaa\x01\x02'+lang_b+b'\xb2\x01 1d8ec0240ede109973f3321b9354b44d\xba\x01\x014\xc2\x01\x08Handheld\xca\x01\x10Asus ASUS_I005DA\xea\x01@afcfbf13334be42036e4f742c80b956344bed760ac91b3aff9b607a610ab4390\xf0\x01\x01\xca\x02\nATM Mobils\xd2\x02\x04WIFI\xca\x03 7428b253defc164018c604a1ebbfebdf\xe0\x03\xa8\x81\x02\xe8\x03\xf6\xe5\x01\xf0\x03\xaf\x13\xf8\x03\x84\x07\x80\x04\xe7\xf0\x01\x88\x04\xa8\x81\x02\x90\x04\xe7\xf0\x01\x98\x04\xa8\x81\x02\xc8\x04\x01\xd2\x04=/data/app/com.dts.freefireth-PdeDnOilCSFn37p1AH_FLg==/lib/arm\xe0\x04\x01\xea\x04_2087f61c19f57f2af4e7feff0b24d9d9|/data/app/com.dts.freefireth-PdeDnOilCSFn37p1AH_FLg==/base.apk\xf0\x04\x03\xf8\x04\x01\x8a\x05\x0232\x9a\x05\n2019118692\xb2\x05\tOpenGLES2\xb8\x05\xff\x7f\xc0\x05\x04\xe0\x05\xf3F\xea\x05\x07android\xf2\x05pKqsHT5ZLWrYljNb5Vqh//yFRlaPHSO9NWSQsVvOmdhEEn7W+VHNUK+Q+fduA3ptNrGB0Ll0LRz3WW0jOwesLj6aiU7sZ40p8BfUE/FI/jzSTwRe2\xf8\x05\xfb\xe4\x06\x88\x06\x01\x90\x06\x01\x9a\x06\x014\xa2\x06\x014\xb2\x06"GQ@O\x00\x0e^\x00D\x06UA\x0ePM\r\x13hZ\x07T\x06\x0cm\\V\x0ejYV;\x0bU5'
    data = payload
    data = data.replace('afcfbf13334be42036e4f742c80b956344bed760ac91b3aff9b607a610ab4390'.encode(),access_token.encode())
    data = data.replace('1d8ec0240ede109973f3321b9354b44d'.encode(),open_id.encode())
    d = encrypt_api(data.hex())

    Final_Payload = bytes.fromhex(d)
    if region.lower == "me":
        URL = "https://loginbp.common.ggbluefox.com/MajorLogin"
    else:
        URL = "https://loginbp.ggblueshark.com/MajorLogin"
    
    try:
        RESPONSE = requests.post(URL, headers=headers, data=Final_Payload, verify=False) 
        
        if RESPONSE.status_code == 200:
            if len(RESPONSE.text) < 10:
                return False

            json_result = get_available_room(RESPONSE.content.hex())
            parsed_data = json.loads(json_result)
            BASE64_TOKEN = parsed_data['8']['data']

            second_dot_index = BASE64_TOKEN.find(".", BASE64_TOKEN.find(".") + 1)     
            BASE64_TOKEN = BASE64_TOKEN[:second_dot_index+44]
            dat = GET_PAYLOAD_BY_DATA(BASE64_TOKEN,access_token,1,response , status_code , name , uid , password, region)
            return dat
    except:
        return None



import os
import json
import base64
from datetime import datetime

import os
import json
import shutil
from datetime import datetime
import threading
file_lock = threading.Lock()

import os, json, shutil, base64
from datetime import datetime
from threading import Lock

file_lock = Lock()

# --- Colors ---
GREEN = "\033[32m"
LIGHT_CYAN = "\033[96m"
LIGHT_YELLOW = "\033[93m"
LIGHT_GREEN = "\033[92m"
NEON_PURPLE = "\033[95m"
LIGHT_RED = "\033[91m"
LIGHT_MAGENTA = "\033[95m"
BRIGHT = "\033[1m"
RESET = "\033[0m"

# Dummy encryption

# Detect rare
def detect_real_rarity(name, uid, region):
    uid_len = len(str(uid))
    rarity_type = None
    rarity_score = 0
    reason = None

    if uid_len <= 9:
        rarity_type = "2 DIGIT UID"
        rarity_score = 100
        reason = "Extremely rare 2 digit UID"
    elif uid_len == 3:
        rarity_type = "3 DIGIT UID"
        rarity_score = 900
        reason = "Very rare 3 digit UID"
    elif str(uid).startswith("1") and uid_len <= 6:
        rarity_type = "ULTRA RARE UID"
        rarity_score = 90
        reason = "Old generation UID"
    elif str(uid).startswith("10") or str(uid).startswith("11"):
        rarity_type = "OG ACCOUNT"
        rarity_score = 85
        reason = "Old region based UID"
    if len(name) <= 4:
        rarity_type = "LEGENDARY NAME"
        rarity_score = 80
        reason = "Very short rare name"

    return rarity_type, rarity_score, reason

# Print rare
def print_rare_account(name, uid, region, rarity_type, rarity_score, reason):
    print(f"\n{LIGHT_MAGENTA}{BRIGHT}💎 RARE ACCOUNT FOUND!{RESET}")
    print(f"{LIGHT_MAGENTA}🎯 Type: {rarity_type}{RESET}")
    print(f"{LIGHT_MAGENTA}⭐ Rarity Score: {rarity_score}{RESET}")
    print(f"{LIGHT_MAGENTA}👤 Name: {name}{RESET}")
    print(f"{LIGHT_MAGENTA}🆔 UID: {uid}{RESET}")
    print(f"{LIGHT_MAGENTA}📝 Reason: {reason}{RESET}")
    print(f"{LIGHT_MAGENTA}🌍 Region: {region}{RESET}\n")

# Print couple
def print_couples_found(account1, account2, reason):
    color = LIGHT_CYAN
    print(f"\n{color}{BRIGHT}💑 COUPLES ACCOUNT FOUND!{RESET}")
    print(f"{color}📝 Reason: {reason}{RESET}")
    print(f"{color}👤 Account 1: {account1['name']} (UID: {account1['uid']}){RESET}")
    print(f"{color}👤 Account 2: {account2['name']} (UID: {account2['uid']}){RESET}")
    print(f"{color}🌍 Region: {account1.get('region', 'N/A')}{RESET}\n")

# Couple detection
def is_couple_uid(uid1, uid2):
    """
    Detect couple UIDs properly.
    Rules:
    - Must have same length
    - 10-digit UID: last 3 digits must match or difference <=1-2 for sequential couple
    - 8-9 digit UID: last 2 digits must match
    - 11-digit UID: very strict, last 3-4 digits must match
    """
    uid1 = str(uid1)
    uid2 = str(uid2)

    if len(uid1) != len(uid2):
        return False

    # Exact match for last few digits
    if len(uid1) == 10:
        return abs(int(uid1[-3:]) - int(uid2[-3:])) <= 1  # strict sequential
    elif len(uid1) in [8, 9]:
        return uid1[-2:] == uid2[-2:]
    elif len(uid1) == 11:
        return abs(int(uid1[-4:]) - int(uid2[-4:])) <= 1  # super strict
    return False

# --- MAIN FUNCTION ---
import os
import json
import base64
import requests
from datetime import datetime
from threading import Lock

file_lock = Lock()
jwt_results = []

def generate_jwt(uid, password):
    url = f"https://fast-jwt-token-api.vercel.app/token?uid={uid}&password={password}"

    try:
        r = requests.get(url, timeout=10)

        if r.status_code == 200:
            data = r.json()

            # FIXED KEY
            token = data.get("jwt_token")

            if token:
                print(f"🔥 JWT Generated → {uid}")

                jwt_results.append({
                    "uid": uid,
                    "password": password,
                    "token": token
                })

                # real-time save
                with open("jwt_token.json", "w", encoding="utf-8") as f:
                    json.dump(jwt_results, f, indent=4, ensure_ascii=False)

                return token
            else:
                print(f"❌ JWT not found → {uid}")
        else:
            print(f"❌ API Error {r.status_code} → {uid}")

    except Exception as e:
        print(f"❌ Failed JWT → {uid} | {e}")
        

def GET_PAYLOAD_BY_DATA(JWT_TOKEN, NEW_ACCESS_TOKEN, date, response, status_code, name, uid, password, region, game_uid=None):
    try:
        # --- Decode JWT payload ---
        token_payload_base64 = JWT_TOKEN.split('.')[1]
        token_payload_base64 += '=' * ((4 - len(token_payload_base64) % 4) % 4)
        decoded_payload = base64.urlsafe_b64decode(token_payload_base64).decode('utf-8')
        decoded_payload = json.loads(decoded_payload)
        NEW_EXTERNAL_ID = decoded_payload['external_id']
        SIGNATURE_MD5 = decoded_payload['signature_md5']

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # --- Payload manipulation ---
        PAYLOAD = b':\x071.120.2\xaa\x01\x02ar\xb2\x01 55ed759fcf94f85813e57b2ec8492f5c\xba\x01\x014\xea\x01@6fb7fdef8658fd03174ed551e82b71b21db8187fa0612c8eaf1b63aa687f1eae\x9a\x06\x014\xa2\x06\x014'
        PAYLOAD = PAYLOAD.replace(b"2023-12-24 04:21:34", now.encode())
        PAYLOAD = PAYLOAD.replace(b"15f5ba1de5234a2e73cc65b6f34ce4b299db1af616dd1dd8a6f31b147230e5b6", NEW_ACCESS_TOKEN.encode("utf-8"))
        PAYLOAD = PAYLOAD.replace(b"4666ecda0003f1809655a7a8698573d0", NEW_EXTERNAL_ID.encode("utf-8"))
        PAYLOAD = PAYLOAD.replace(b"7428b253defc164018c604a1ebbfebdf", SIGNATURE_MD5.encode("utf-8"))
        PAYLOAD = PAYLOAD.hex()
        PAYLOAD = encrypt_api(PAYLOAD)
        PAYLOAD = bytes.fromhex(PAYLOAD)

        # --- Account data ---
        account_data = {
            "uid": uid,
            "password": password,
            "name": name,
            "game_uid": game_uid if game_uid else "",
            "region": region,
            "access_token": NEW_ACCESS_TOKEN
        }

        # --- Generate JWT real-time ---
        jwt_token = generate_jwt(uid, password)
        if jwt_token:
            account_data["jwt_token"] = jwt_token

        with file_lock:
            # --- Region accounts ---
            region_file = f"{region}.json"
            region_data = []
            if os.path.exists(region_file):
                with open(region_file, "r", encoding="utf-8") as rf:
                    try:
                        region_data = json.load(rf)
                        if not isinstance(region_data, list):
                            region_data = []
                    except:
                        region_data = []

            # --- Couple accounts ---
            couple_file = "couple_accounts.json"
            couple_data = []
            if os.path.exists(couple_file):
                with open(couple_file, "r", encoding="utf-8") as cf:
                    try:
                        couple_data = json.load(cf)
                        if not isinstance(couple_data, list):
                            couple_data = []
                    except:
                        couple_data = []

            # --- Check for couple ---
            couple_found = False
            for acc in region_data:
                if is_couple_uid(acc["uid"], uid):
                    reason = f"Sequential UID pattern: {acc['uid']} & {uid}"
                    couple_entry = {
                        "couple_id": f"{acc['uid']}_{uid}",
                        "account1": {
                            "uid": acc["uid"],
                            "password": acc["password"],
                            "name": acc["name"],
                            "account_id": str(acc["uid"]),
                            "thread_id": 1
                        },
                        "account2": {
                            "uid": uid,
                            "password": password,
                            "name": name,
                            "account_id": str(uid),
                            "thread_id": 1
                        },
                        "reason": reason,
                        "region": region,
                        "date_matched": now
                    }
                    if not any(c["couple_id"] == couple_entry["couple_id"] for c in couple_data):
                        couple_data.append(couple_entry)
                        with open(couple_file + ".tmp", "w", encoding="utf-8") as cf:
                            json.dump(couple_data, cf, indent=4, ensure_ascii=False)
                        os.replace(couple_file + ".tmp", couple_file)
                    print_couples_found(acc, account_data, reason)
                    couple_found = True
                    break

            # --- Save region account ---
            if not any(acc.get("uid") == uid for acc in region_data):
                region_data.append(account_data)
                with open(region_file + ".tmp", "w", encoding="utf-8") as rf:
                    json.dump(region_data, rf, indent=4, ensure_ascii=False)
                os.replace(region_file + ".tmp", region_file)

        # --- Rare accounts ---
        rarity_type, rarity_score, reason = detect_real_rarity(name, uid, region)
        if rarity_type:
            rare_file = "rare_accounts.json"
            rare_data = []
            if os.path.exists(rare_file):
                with open(rare_file, "r", encoding="utf-8") as rf:
                    try:
                        rare_data = json.load(rf)
                        if not isinstance(rare_data, list):
                            rare_data = []
                    except:
                        rare_data = []
            if not any(acc.get("uid") == uid for acc in rare_data):
                rare_data.append(account_data)
                with open(rare_file + ".tmp", "w", encoding="utf-8") as rf:
                    json.dump(rare_data, rf, indent=4, ensure_ascii=False)
                os.replace(rare_file + ".tmp", rare_file)
            print_rare_account(name, uid, region, rarity_type, rarity_score, reason)
        else:
            if not couple_found:
                print(
                    f"\n{GREEN}{BRIGHT}🥳 ACCOUNT GENERATED{RESET}\n"
                    f"{LIGHT_CYAN}{BRIGHT}🆔 UID        : {uid}{RESET}\n"
                    f"{LIGHT_YELLOW}{BRIGHT}🔐 PASSWORD   : {password}{RESET}\n"
                    f"{LIGHT_GREEN}{BRIGHT}💡 NAME       : {name}{RESET}\n"
                    f"{NEON_PURPLE}{BRIGHT}🌏 REGION     : {region}{RESET}\n"
                    f"{LIGHT_RED}{BRIGHT}🎯 GAME UID   : {game_uid if game_uid else 'N/A'}{RESET}\n"
                )

        return account_data

    except Exception as e:
        print(f"❌ Error in Payload: {e}")
        return None
        
def parse_results(parsed_results):
    result_dict = {}
    for result in parsed_results:
        field_data = {}
        field_data['wire_type'] = result.wire_type
        if result.wire_type == "varint":
            field_data['data'] = result.data
        if result.wire_type == "string":
            field_data['data'] = result.data
        if result.wire_type == "bytes":
            field_data['data'] = result.data
        elif result.wire_type == 'length_delimited':
            field_data["data"] = parse_results(result.data.results)
        result_dict[result.field] = field_data
    return result_dict


def get_available_room(input_text):
    try:
        parsed_results = Parser().parse(input_text)
        parsed_results_objects = parsed_results
        parsed_results_dict = parse_results(parsed_results_objects)
        json_data = json.dumps(parsed_results_dict)
        return json_data
    except Exception as e:
        return None

def GET_LOGIN_DATA(JWT_TOKEN, PAYLOAD, region):
    if region.lower() == "me":
        url = 'https://clientbp.ggblueshark.com/GetLoginData'
    else:
        link = get_region_url(region)
        url = f"{link}GetLoginData"

    headers = {
        'Expect': '100-continue',
        'Authorization': f'Bearer {JWT_TOKEN}',
        'X-Unity-Version': '2018.4.11f1',
        'X-GA': 'v1 1',
        'ReleaseVersion': 'OB53',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 10; G011A Build/PI)',
        'Host': 'clientbp.ggblueshark.com',
        'Connection': 'close',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    
    try:
        response = requests.post(url, headers=headers, data=PAYLOAD, verify=False)
        response.raise_for_status()    
        x = response.content.hex()
        json_result = get_available_room(x)
               # 1. Ye wahi purana fix hai (ensure karein ki ye sahi jagah hai)
        return json_result
    except Exception as e:
        return None

# ==========================================
# UNLIMITED AUTO-MAKER (NO TELEGRAM - FAST MODE)
# ==========================================

import threading
import time
import sys

# Settings

THREAD_COUNT = 50  # Speed: 5-10 rakhein (Jyada karne par device heat ho sakta hai)

# --- Fast Auto Maker Function ---
def auto_account_maker(thread_index):
    # print(f"{purpel}Thread-{thread_index} Started...{bold}") 
    consecutive_fails = 0
    
    while True:
        try:
            # Account create karne ki koshish
            result = create_acc(TARGET_REGION)
            
            if result:
                consecutive_fails = 0
                print(f"{green}{BRIGHT}[Thread-{thread_index}] 🎉 Account Created!{bold}")
                # No Sleep here for maximum speed
            else:
                consecutive_fails += 1
                
                # Agar IP Block ho jaye (Too many requests)
                if consecutive_fails >= 10: 
                    print(f"{purpel}{BRIGHT}[Thread-{thread_index}] 👾 IP Ratelimited. Waiting 10s...{bold}")
                    time.sleep(10)
                    consecutive_fails = 0
                else:
                    # Fail hone par turant retry (Fast)
                    pass
                    
        except Exception as e:
            # Error aane par thoda rukna safe hai
            time.sleep(1)
# =====================
# COLORS (ALWAYS TOP)
# =====================
import threading
import time
import sys
import os

RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
CYAN = "\033[96m"
PURPLE = "\033[95m"
LIGHT_RED = "\033[91m"
LIGHT_GREEN = "\033[92m"
LIGHT_YELLOW = "\033[93m"
LIGHT_CYAN = "\033[96m"
NEON_PURPLE = "\033[95m"
RESET = "\033[0m"
BRIGHT = "\033[1m"

# =====================
# COLORS
# =====================
MAGENTA      = "\033[95m"
LIGHT_GREEN  = "\033[92m"
LIGHT_YELLOW = "\033[93m"
LIGHT_CYAN   = "\033[96m"
LIGHT_RED    = "\033[91m"
RESET        = "\033[0m"
BRIGHT       = "\033[1m"

# NEW COLORS
# =====================

LIGHT_PURPLE   = "\033[38;5;135m"   # lavender/purple
LIGHT_PINK     = "\033[38;5;205m"   # hot pink
LIGHT_TEAL     = "\033[38;5;80m"    # teal / cyan variant
LIGHT_LIME     = "\033[38;5;118m"   # lime green
LIGHT_AQUA     = "\033[38;5;51m"    # aqua blue
LIGHT_BROWN    = "\033[38;5;94m"    # brownish
LIGHT_GRAY     = "\033[38;5;250m"   # light gray
LIGHT_MAGENTA2 = "\033[38;5;201m"   # magenta variant
LIGHT_YELLOW2  = "\033[38;5;226m"   # bright yellow

RESET          = "\033[0m"
BRIGHT         = "\033[1m"
# =====================
# ANOTHER 10 NEW COLORS
# =====================
LIGHT_RED2      = "\033[38;5;196m"  # intense red
LIGHT_ORANGE2   = "\033[38;5;214m"  # bright orange
LIGHT_YELLOW3   = "\033[38;5;220m"  # golden yellow
LIGHT_GREEN2    = "\033[38;5;46m"   # bright green
LIGHT_CYAN2     = "\033[38;5;51m"   # vivid cyan
LIGHT_BLUE2     = "\033[38;5;33m"   # deep blue
LIGHT_PURPLE2   = "\033[38;5;141m"  # soft purple
LIGHT_MAGENTA3  = "\033[38;5;201m"  # pinkish magenta
LIGHT_BROWN2    = "\033[38;5;130m"  # brown
LIGHT_GRAY2     = "\033[38;5;245m"  # silver gray

RESET           = "\033[0m"
BRIGHT          = "\033[1m"
# =====================
# 10 BRAND NEW VIBRANT COLORS
# =====================
COLOR_1  = "\033[38;5;196m"  # Vivid Red
COLOR_2  = "\033[38;5;208m"  # Orange
COLOR_3  = "\033[38;5;226m"  # Bright Yellow
COLOR_4  = "\033[38;5;46m"   # Bright Green
COLOR_5  = "\033[38;5;51m"   # Aqua / Cyan
COLOR_6  = "\033[38;5;21m"   # Royal Blue
COLOR_7  = "\033[38;5;201m"  # Hot Pink
COLOR_8  = "\033[38;5;93m"   # Purple
COLOR_9  = "\033[38;5;214m"  # Gold / Deep Orange
COLOR_10 = "\033[38;5;240m"  # Light Gray / Silver

RESET    = "\033[0m"
BRIGHT   = "\033[1m"

# =====================
# BRAND NEW COLOR PALETTE
# =====================

NEON_RED        = "\033[38;5;197m"   # Neon Red
NEON_ORANGE     = "\033[38;5;214m"   # Neon Orange
NEON_YELLOW     = "\033[38;5;226m"   # Neon Yellow
NEON_GREEN      = "\033[38;5;82m"    # Neon Green
NEON_CYAN       = "\033[38;5;51m"    # Neon Cyan
NEON_BLUE       = "\033[38;5;27m"    # Neon Blue
NEON_MAGENTA    = "\033[38;5;201m"   # Neon Magenta
NEON_PINK       = "\033[38;5;213m"   # Hot Neon Pink
NEON_PURPLE     = "\033[38;5;99m"    # Electric Purple
NEON_LIME       = "\033[38;5;118m"   # Neon Lime Green

BRIGHT_TEAL     = "\033[38;5;44m"    # Bright Teal
BRIGHT_INDIGO   = "\033[38;5;63m"    # Bright Indigo
BRIGHT_PEACH    = "\033[38;5;217m"   # Bright Peach
BRIGHT_CORAL    = "\033[38;5;209m"   # Bright Coral
BRIGHT_AQUA     = "\033[38;5;51m"    # Bright Aqua
BRIGHT_VIOLET   = "\033[38;5;141m"   # Bright Violet
BRIGHT_MINT     = "\033[38;5;120m"   # Bright Mint
BRIGHT_ORCHID   = "\033[38;5;183m"   # Bright Orchid
BRIGHT_SALMON   = "\033[38;5;210m"   # Bright Salmon
BRIGHT_AMBER    = "\033[38;5;214m"   # Bright Amber

RESET_COLOR     = "\033[0m"
BRIGHT          = "\033[1m"
# =====================
# MAIN
# =====================

# =====================
# SETTINGS
# =====================
THREAD_COUNT = 15
#ACCOUNTS_FILE = "accounts.txt"
TARGET_REGION = None  # will be set via menu

# =====================
# AUTO MAKER
# auto_account_maker() আগের মতোই থাকবে
# =====================
def start_guest_creator():
    global TARGET_REGION
    print(f"\n{LIGHT_GREEN}{BRIGHT} 🎀 Starting Guest Account Creation for {LIGHT_RED2}{BRIGHT}{TARGET_REGION}...{RESET}\n")

    for i in range(THREAD_COUNT):
        t = threading.Thread(target=auto_account_maker, args=(i+1,))
        t.daemon = True
        t.start()

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print(f"\n{LIGHT_RED}{BRIGHT} ⛔ Guest creation interrupted by user.{RESET}")


ACCOUNTS_FILE = "accounts.json"  # json file

def view_accounts():
    print(f"\n{MAGENTA}{BRIGHT}========== ⚠️SAVED ACCOUNTS =========={RESET}\n")

    if not os.path.exists(ACCOUNTS_FILE):
        print(f"{LIGHT_RED}{BRIGHT} ⚠️accounts.json not found!{RESET}")
        return

    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
        try:
            accounts = json.load(f)
        except:
            accounts = []

    if not accounts:
        print(f"{LIGHT_RED}{BRIGHT} ⚠️No accounts saved yet!{RESET}")
        return

    for i, acc in enumerate(accounts, start=1):
        uid = acc.get("uid", "N/A")
        password = acc.get("password", "N/A")
        name = acc.get("name", "N/A")
        game_uid = acc.get("game_uid", "N/A") or "N/A"

        print(f"{LIGHT_GREEN}{i}.{RESET} {LIGHT_CYAN}UID:{uid} | password:{password} | Name:{name} | Game UID:{game_uid}{RESET}")

    print(f"\n{MAGENTA}===================================={RESET}\n")


def reset_accounts():
    print(f"\n{LIGHT_RED}{BRIGHT} ⚠️WARNING! This will delete ALL accounts!{RESET}")
    confirm = input(f"{LIGHT_YELLOW}{BRIGHT} 🤔 Are you sure? (y/n): {RESET}").strip().lower()

    if confirm == "y":
        open(ACCOUNTS_FILE, "w", encoding="utf-8").close()
        print(f"{LIGHT_GREEN}{BRIGHT} ☑️ All accounts reset successfully!{RESET}")
    else:
        print(f"{LIGHT_RED}{BRIGHT}🤕 Reset cancelled.{RESET}")

import random

# =====================
# ABOUT SECTION
# =====================
def get_random_color():
    colors = [
        LIGHT_RED, LIGHT_RED2, LIGHT_ORANGE2, LIGHT_YELLOW, LIGHT_YELLOW2, LIGHT_YELLOW3,
        LIGHT_GREEN, LIGHT_GREEN2, LIGHT_CYAN, LIGHT_CYAN2, LIGHT_BLUE2, LIGHT_PURPLE,
        LIGHT_MAGENTA2, LIGHT_MAGENTA3, LIGHT_PINK, LIGHT_TEAL, LIGHT_LIME, LIGHT_AQUA,
        NEON_RED, NEON_YELLOW, NEON_GREEN, NEON_PINK, NEON_PURPLE, NEON_ORANGE
    ]
    return random.choice(colors)

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def wait_for_enter():
    input(f"\n{LIGHT_CYAN}{BRIGHT}Press ENTER to return to the menu...{RESET}")

def about_section():
    clear_screen()

    print(f"{MAGENTA}=========================================={RESET}")
    print(f"{LIGHT_GREEN}{BRIGHT}  👑 JXE Account Generator - {LIGHT_RED2}{BRIGHT}ABOUT{RESET}")
    print(f"{MAGENTA}=========================================={RESET}\n")

    print(f"{LIGHT_RED2}{BRIGHT}  About This Tool:{RESET}")
    print(f"{LIGHT_GREEN}{BRIGHT}• Generate Free Fire guest accounts for multiple regions")
    print(f"{COLOR_4}{BRIGHT}• GHOST mode for special accounts")
    print(f"{COLOR_4}{BRIGHT}• Automatic JWT token generation")
    print(f"{COLOR_4}{BRIGHT}• Multi-threaded account creation")
    print(f"{COLOR_4}{BRIGHT}• Safe account storage in JSON / text files")
    print(f"{COLOR_4}{BRIGHT}• Thread-safe file operations for reliability\n")

    print(f"{NEON_YELLOW}{BRIGHT}📁 Storage Locations:{RESET}")
    print(f"{LIGHT_GREEN}{BRIGHT}• Accounts file: accounts.txt")
    print(f"{COLOR_4}{BRIGHT}• JWT Tokens:  (if used)")
    print(f"{COLOR_4}{BRIGHT}• GHOST Accounts: ghost_accounts.txt\n")

    print(f"{LIGHT_RED2}{BRIGHT}⚠️ Disclaimer:{RESET}")
    print(f"{LIGHT_RED2}{BRIGHT}This tool is for educational purposes only.")
    print(f"{LIGHT_RED2}{BRIGHT}Use it responsibly at your own risk.\n")

    print(f"{NEON_YELLOW}{BRIGHT}Dekho, Isme Sare Accounts Save honge: Rare, Couple, Normal — Sb Alg Alg Folders mein. Aur agar bychance koi Rare id miss ho jata hai, to wo Normal Account ke Folder me save hoga.{RESET}\n")
    print(f"{NEON_YELLOW}{BRIGHT}⚠️ Agar IP ban hota hai, to agar WiFi use nahi kar rahe ho, to Aeroplane mode ON/OFF karo. Nahi to VPN use karo.{RESET}\n")
    print(f"{NEON_YELLOW}{BRIGHT}💡 Agar kiska generate nahi ho paa raha, to option 11 try karo Ghost Mode, mtlb ki all server phir usko jaha IP se login karoge, vaha lock ho jayegi id.{RESET}\n")

    wait_for_enter()

# =====================
# MENU
# =====================
def menu():
    print(f"""
{MAGENTA}=========================================={RESET}
{NEON_RED}{BRIGHT}1{RESET}{LIGHT_YELLOW}{BRIGHT}. START GUEST ACCOUNT CREATE
{NEON_RED}{BRIGHT}2{RESET}{LIGHT_GREEN2}. VIEW ACCOUNTS
{NEON_RED}{BRIGHT}3{RESET}{NEON_BLUE}{BRIGHT}. RESET ACCOUNTS
{NEON_RED}{BRIGHT}4{RESET}{NEON_CYAN}{BRIGHT}. ABOUT
{NEON_RED}{BRIGHT}5{RESET}{LIGHT_RED2}{BRIGHT}. EXIT
{MAGENTA}=========================================={RESET}
""")

    choice = input(f"{LIGHT_RED}{BRIGHT} 🎯 Select Option: {RESET}").strip()
    return choice


# =====================
# REGION SELECTION
# =====================
# =====================
def select_region():
    regions = {
        "1": "IND", "2": "US", "3": "EU", "4": "SG",
        "5": "BD", "6": "OTHER", "7": "UK", "8": "CA",
        "9": "AU", "10": "NZ", "11": "JP", "12": "KR",
        "13": "CN", "14": "BR", "15": "MX", "16": "ZA",
        "17": "AE", "18": "RU", "19": "FR", "20": "DE",
        "21": "IT"
    }

    lang_map = {
        "IND": "hi", "US": "en", "EU": "en", "SG": "en",
        "BD": "bn", "OTHER": "en", "UK": "en", "CA": "en",
        "AU": "en", "NZ": "en", "JP": "ja", "KR": "ko",
        "CN": "zh", "BR": "pt", "MX": "es", "ZA": "en",
        "AE": "ar", "RU": "ru", "FR": "fr", "DE": "de",
        "IT": "it", "ME": "ar", "ID": "id", "VN": "vi",
        "TH": "th", "PK": "ur", "TW": "zh", "CIS": "ru",
        "NA": "en", "SAC": "es"
    }

    
    print(f"""
{MAGENTA}================ Select Target Region ================{RESET}
{LIGHT_CYAN}1. {LIGHT_GREEN2}{BRIGHT}India {LIGHT_YELLOW}{BRIGHT}(IND){RESET}
{LIGHT_CYAN}2. {LIGHT_RED2}{BRIGHT}USA {LIGHT_BLUE2}{BRIGHT}(US){RESET}
{LIGHT_CYAN}3. {BRIGHT_ORCHID}{BRIGHT}Europe {BRIGHT_CORAL}{BRIGHT}(EU){RESET}
{LIGHT_CYAN}4. {LIGHT_YELLOW3}{BRIGHT}Singapore {BRIGHT_ORCHID}{BRIGHT}(SG){RESET}
{LIGHT_CYAN}5. {LIGHT_GREEN2}{BRIGHT}Bangladesh {NEON_RED}{BRIGHT}(BD){RESET}
{LIGHT_CYAN}6. {LIGHT_BLUE2}{BRIGHT}Other{RESET}
{LIGHT_CYAN}7. {LIGHT_PURPLE}{BRIGHT}United Kingdom {COLOR_7}{BRIGHT}(UK){RESET}
{LIGHT_CYAN}8. {BRIGHT_INDIGO}{BRIGHT}Canada{LIGHT_CYAN2}{BRIGHT}(CA){RESET}
{LIGHT_CYAN}9. {NEON_YELLOW}{BRIGHT}Australia {BRIGHT_AMBER}{BRIGHT}(AU){RESET}
{LIGHT_CYAN}10. {COLOR_1} {BRIGHT}Zealand {LIGHT_PINK}{BRIGHT}(NZ){RESET}
{LIGHT_CYAN}11. {NEON_GREEN}{BRIGHT}Japan {BRIGHT_AQUA}{BRIGHT}(JP){RESET}
{LIGHT_CYAN}12. {COLOR_7}{BRIGHT}South Korea {LIGHT_LIME}{BRIGHT}(KR){RESET}
{LIGHT_CYAN}13. {LIGHT_BLUE2}{BRIGHT}China {NEON_RED}{BRIGHT}(CN){RESET}
{LIGHT_CYAN}14. {BRIGHT_MINT}{BRIGHT}Brazil {NEON_PINK}{BRIGHT}(BR){RESET}
{LIGHT_CYAN}15. {LIGHT_BLUE2}{BRIGHT}Mexico {BRIGHT_PEACH}{BRIGHT}(MX){RESET}
{LIGHT_CYAN}16. {LIGHT_YELLOW2}{BRIGHT}South Africa {BRIGHT_TEAL}{BRIGHT}(ZA){RESET}
{LIGHT_CYAN}17. {BRIGHT_VIOLET}{BRIGHT}United Arab Emirates {BRIGHT_PEACH}{BRIGHT}(AE){RESET}
{LIGHT_CYAN}18. {LIGHT_YELLOW2}{BRIGHT}Russia {COLOR_1}{BRIGHT}(RU){RESET}
{LIGHT_CYAN}19. {LIGHT_MAGENTA3}{BRIGHT}France {LIGHT_YELLOW}{BRIGHT}(FR){RESET}
{LIGHT_CYAN}20. {NEON_RED}{BRIGHT}Germany {NEON_GREEN}{BRIGHT}(DE){RESET}
{LIGHT_CYAN}21. {LIGHT_GREEN2}{BRIGHT}Italy {LIGHT_BLUE2}{BRIGHT}(IT){RESET}
{MAGENTA}==================================================={RESET}
""")

    
    while True:
        choice = input(f"{LIGHT_YELLOW}{BRIGHT}🌏 Select Region: {RESET}").strip()
        region = regions.get(choice)
        if region:
            lang = lang_map.get(region, "en")  # default English
            print(f"\n{LIGHT_GREEN}{BRIGHT}🥶 Target region set to: {LIGHT_RED2}{BRIGHT}{region} | Lang: {lang}{RESET}\n")
            return region, lang
        else:
            print(f"{LIGHT_RED}{BRIGHT}⚠️ Invalid option! Please try again.{RESET}\n")
# =====================
# MAIN
# =====================
if __name__ == "__main__":

    print(f"{MAGENTA}=========================================={RESET}")
    print(f"{LIGHT_GREEN}{BRIGHT}  👾 GUEST MAKER {NEON_PURPLE}{BRIGHT}💥 VERSION 7.9 - {LIGHT_AQUA}{BRIGHT}RUNNING{RESET}")
    print(f"{NEON_RED}{BRIGHT}  📵 Threads: {THREAD_COUNT} | {NEON_YELLOW}{BRIGHT}🌏 Region: Not set yet{RESET}")
    print(f"{MAGENTA}=========================================={RESET}")

    TARGET_REGION = None  # Initialize region as None

    try:
        while True:
            opt = menu()

            if opt == "1":
                # Ask for region if not already set
                if not TARGET_REGION:
                    TARGET_REGION, lang = select_region()
                    if not TARGET_REGION:
                        continue  # invalid region, go back to menu

                    print(f"{LIGHT_YELLOW}🌏 Current Target Region: {LIGHT_RED2}{BRIGHT}{TARGET_REGION} | Lang: {lang}{RESET}\n")

                # Ask for user confirmation before starting
                confirm = input(f"{LIGHT_CYAN}{BRIGHT}♻️ Ready to start account creation for {LIGHT_RED2}{BRIGHT}{TARGET_REGION}? (y/n): {RESET}").strip().lower()
                if confirm == "y":
                    start_guest_creator()
                else:
                    print(f"{LIGHT_RED}⚠️ Account creation cancelled. You can select another option.{RESET}\n")

            elif opt == "2":
                view_accounts()

            elif opt == "3":
                reset_accounts()

            elif opt == "4":
                about_section()  # Show about info

            elif opt == "5":
                print(f"{LIGHT_RED}{BRIGHT} 🤖 Exiting... Bye!{RESET}")
                sys.exit(0)

            else:
                print(f"{LIGHT_RED}{BRIGHT} ⚠️Invalid Option! Try again.{RESET}")

    except KeyboardInterrupt:
        print(f"\n{LIGHT_RED}{BRIGHT} ⛔ Script interrupted by user. Exiting...{RESET}")
        sys.exit(0)