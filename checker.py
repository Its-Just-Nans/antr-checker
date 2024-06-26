import requests
from hashlib import sha256
from json import dumps, loads
from os.path import exists
from dotenv import load_dotenv
from os import getenv

load_dotenv()

SECRET_LOGIN = getenv("SECRET_LOGIN")
DATA = "data.json"
URL_WEBHOOK = getenv("WEBHOOK_URL")

# login to get the cookie
login = requests.get(SECRET_LOGIN)
cookie = login.history[0].cookies["PHPSESSID"]


def make_sha(item):
    j = dumps(item, indent=4)
    m = sha256()
    m.update(j.encode())
    return m.hexdigest()


def load_data():
    if not exists(DATA):
        with open(DATA, "w") as file:
            file.write("[]")
    try:
        with open(DATA, "r") as file:
            loaded = loads(file.read())
    except Exception as _e:
        loaded = []
    return loaded


# get the data
response = requests.post(
    "https://offres-et-candidatures-cifre.anrt.asso.fr/espace-membre/offre/dtList",
    cookies={
        "PHPSESSID": cookie,
    },
    headers={
        "Content-Type": "application/x-www-form-urlencoded",
    },
    data={
        "draw": "1",
        "offreType": "entreprise",
    },
)


def notify(text):
    requests.post(
        URL_WEBHOOK,
        json={
            "username": "ANTR checker",
            "content": text,
            "avatar_url": "https://offres-et-candidatures-cifre.anrt.asso.fr/public/images/logos/logo-cifre-s.png",
        },
    )


current_data = load_data()
to_add = []
try:
    resp = response.json()
except Exception as _e:
    resp = {}

if "data" not in resp:
    notify("Invalid cookie")
    exit(1)

resp = resp["data"]

for one_item in resp:
    shaed = str(make_sha(one_item))
    if shaed not in current_data:
        smol_item = f"{one_item['titre']}\n{one_item['ville']} - {one_item['rs']}\nhttps://offres-et-candidatures-cifre.anrt.asso.fr/espace-membre/offre/detail/{one_item['crypt']}"
        notify(smol_item + "\n-------------------")
        print("New item found")
        to_add.append(shaed)


final = current_data + to_add

with open(DATA, "w") as file:
    txt = dumps(final, indent=4)
    file.write(txt)
