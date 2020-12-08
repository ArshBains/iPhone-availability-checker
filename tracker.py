import requests
import smtplib
import ssl
import time
from datetime import datetime
import re
import sys

interval = 10    # log interval in minutes
email_cycles = 6    # interval after which email is sent => (interval * email_cycles) minutes

port = 465
bot_email = "bot@gmail.com"
password = "iamabot"
smtp_server = "smtp.gmail.com"

iphone_families = {
    1: ["iPhone Xr", "iphonexr"],
    2: ["iPhone 11", "iphone11"],
    3: ["iPhone 12/iPhone 12 mini", "iphone12"],
    4: ["iPhone 12 Pro/ iPhone 12 Pro Max", "iphone12pro"]
}
MODEL_URL = "https://www.apple.com/shop/product-locator-meta?family={0}"
STORES_SEARCH_URL = "https://www.apple.com/shop/retail/pickup-message?pl=true&parts.0={0}&location={1}"


class crayons:
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'


col_width = max(len(family[0]) for family in iphone_families.values()) + 1

print(crayons.YELLOW+"iPhone families"+crayons.ENDC)
for key, value in iphone_families.items():
    value = value[0]
    pad = ""
    padding = col_width - len(value)
    for x in range(padding):
        pad += " "
    value = value + pad
    print(value + ": "+ crayons.RED + str(key)+ crayons.ENDC)

state = True
choosed_family = None
while state:
    try:
        choosed_family = int(input("\nChoose a iPhone family: "))
        if choosed_family not in iphone_families.keys():
            print("Please give valid input")
        else:
            state = False
            print(crayons.CYAN+"Searching available models..."+crayons.ENDC)
    except:
        print("Please give valid input")


search_family_query = iphone_families[choosed_family][1]
# print(search_family_query)
try:
    available_models = requests.get(MODEL_URL.format(search_family_query))  # get request
except:
    print("Connection error")
    sys.exit()
all_models_list = []
try:
    all_models_list = (
        available_models.json()
        .get("body")
        .get("productLocatorOverlayData")
        .get("productLocatorMeta")
        .get("products")
    )
    # print(all_models_list)
except:
    print("Failed to load the models list.\n Please try again later")


ul_models = {}
index = 1
for model in all_models_list:
    if model['carrierModel'] == 'UNLOCKED/US':
        ul_models[index] = [model['productTitle'], model['partNumber']]
        index += 1

# print(ul_models)
if len(ul_models) == 0:
    print("No models found :(")
    sys.exit()

col_width = max(len(family[0]) for family in ul_models.values()) + 1
print(crayons.YELLOW+"\nAvailable models"+crayons.ENDC)
for key, value in ul_models.items():
    value = value[0]
    pad = ""
    padding = col_width - len(value)
    for x in range(padding):
        pad += " "
    value = value + pad
    print(value + ": " + crayons.RED + str(key) + crayons.ENDC)

state = True
choosed_model = None
while state:
    try:
        choosed_model = int(input("\nChoose a model: "))
        if choosed_model not in ul_models.keys():
            print("Please give valid input")
        else:
            state = False
    except:
        print("Please give valid input")

part_number = ul_models[choosed_model][1]
# print(part_number)

zip_code = input("Please enter your zipcode: ")
print(crayons.CYAN+"Finding stores near you..."+crayons.ENDC)
try:
    stores = requests.get(STORES_SEARCH_URL.format(part_number, zip_code))  # get request
except:
    print("Connection error")
    sys.exit()
# print(stores)

if stores.json().get('body').get('errorMessage') != None:
    print("No stores found :(")
    sys.exit()

stores = stores.json().get('body').get('stores')
# print(stores)
stores_dict = {}
index = 1
for store in stores:
    stores_dict[index] = [store['storeName']+", "+store['city'], store['partsAvailability'][part_number]['storeSelectionEnabled'], store['storeNumber']]
    index += 1
# print(stores_dict)
col_width = max(len(store_name[0]) for store_name in stores_dict.values()) + 1
print(crayons.YELLOW+"\nStores near you"+crayons.ENDC)
for key, value in stores_dict.items():
    value = value[0]
    pad = ""
    padding = col_width - len(value)
    for x in range(padding):
        pad += " "
    value = value + pad
    print(value + ": " + crayons.RED + str(key) + crayons.ENDC)

state = True
choosed_store = None
while state:
    try:
        choosed_store = int(input("\nChoose a store: "))
        if choosed_store not in stores_dict.keys():
            print("Please give valid input")
        else:
            state = False
    except:
        print("Please give valid input")

choosed_store = stores_dict[choosed_store]
store_number = choosed_store[2]
# print(choosed_store)
if choosed_store[1]:
    print("Available :)")
else:
    print("Not Available :(")

state = True
track = None
while state:
    try:
        track = input(crayons.BLUE+"\nDo you want to track the availablity?(Y/N)"+crayons.ENDC).lower()
        if track == 'y' or track == 'n':
            state = False
    except:
        print("Please give valid input")

if track == 'n':
    sys.exit()

state = True
r_email = None
email_check = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
while state:
    try:
        r_email = input("\nEnter your email id: ")
        if re.search(email_check, r_email):
            state = False
        else:
            print("Invalid Email")
    except:
        print("Invalid Email")
print(crayons.GREEN+"\nTracker ON\nLOGS:"+crayons.ENDC)

def log_status(status):
    dt = datetime.now()
    message = dt.strftime("%m/%d/%Y %H:%M:%S -> ") + status
    print(message)
    with open("iphone-log.txt", "a") as text_file:
        text_file.write(message + "\n")


def send_email(status):
    message = "Subject: iPhone\n\n" + status
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(bot_email, password)
        server.sendmail(bot_email, r_email, message)


cycle_number = 0
while True:
    try:
        stores = requests.get(STORES_SEARCH_URL.format(part_number, zip_code))  # get request
    except:
        # print("Connection error")
        log_status("Connection error")
        time.sleep(60 * interval)
        continue
    if stores.json().get('body').get('errorMessage')!= None:
        # print("Store not found")
        log_status("Store not found")
        time.sleep(60 * interval)
        continue
    stores = stores.json().get('body').get('stores')
    for store in stores:
        if store['storeNumber'] == store_number:
            availability = store['partsAvailability'][part_number]['storeSelectionEnabled']
    if availability:
        availability = "Available"
    else:
        availability = "Not available"
    log_status(availability)
    if 0 < email_cycles and cycle_number % email_cycles == 0:
        send_email(availability)
    cycle_number += 1
    time.sleep(60*interval)
