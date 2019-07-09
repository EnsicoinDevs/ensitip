#! /usr/bin/python
import json
import translator
import hashlib
import random



def generate_alea_hex():
    return hex(random.randint(0,15))[2:]

def account_exists(name):
    return

def create_new_account(name):

    name = str(name)

    f = open("comptes.json", "r")
    comptes = json.load(f)["comptes"]
    f.close()

    if name in comptes:
        return "il existe déjà un compte lié a votre ID discord. Utilisez 'ensitip voir' pour récupérer ses informations"

    comptes[name]={}

    priv_key = ''
    for _ in range(40):
        priv_key += generate_alea_hex()
    comptes[name]["clef_priv"] = priv_key
    print("clef privée: " + comptes[name]["clef_priv"])

    h = hashlib.new('ripemd160')
    h.update(priv_key.encode())
    comptes[name]["clef_pub"] = h.hexdigest()
    print("clef publique: " + comptes[name]["clef_pub"])

    comptes[name]["solde"] = 0

    comptes[name]["tx_in"] = []

    data = {}
    data["comptes"] = comptes
    f = open("comptes.json", "w")
    f.write(json.dumps(data, indent=4))
    f.close()

    return "compte créé, utilisez 'ensitip voir' pour récupérer ses informations"


def get_accounts():
    f = open("comptes.json", "r")
    comptes = json.load(f)["comptes"]
    f.close()
    return comptes


def get_pub_key(name):
    return get_accounts()[name]["clef_pub"]


def get_priv_key(name):
    return get_accounts()[name]["clef_priv"]


def get_balance(name):
    return get_accounts()[name]["solde"]


def get_tx_in(name):
    liste_de_tx_in = []

    raw_list = get_accounts()[name]["tx_in"]

    for tx in raw_list:

        new_tx_in = translator.Tx_in()
        previous_output = translator.Outpoint()

        thash = tx["hash"]
        index = tx["index"]
        script = tx["script"]

        previous_output.create(thash, index)
        new_tx_in.create(previous_output, script)

        liste_de_tx_in.append(new_tx_in)

    return liste_de_tx_in


def make_tx_out(receiver, amount):
    tx_out = translator.Tx_out()

    pub_key = get_pub_key(receiver)

    script = chr(0x64) + chr(0xa0) + str(hash(pub_key)) + chr(0x78) + chr(0x8c) + chr(0xaa)
    #         OP_DUP    OP_HASH160 <hash160(pubKey)> OP_EQUAL OP_VERIFY OP_CHECKSIG
                                 #CHANGER FCT HASH
    tx_out.create(amount, script)

    return tx_out


def add_tx_in(receiver, tx_out):
    # TODO, sans doute en utilisant grpc
    return "olala"



def reset_tx_in(name):

    f = open("comptes.json", "r")
    comptes = json.load(f)["comptes"]
    f.close()

    comptes[name][tx_in] = []

    f = open("comptes.json", "w")
    json.dump(comptes, f)
    f.close()



    new_tx_in = {}

    new_tx_in["hash"] = hash(tx)
    new_tx_in["index"] = 0
    new_tx_in["script"] = sign(tx, get_priv_key(name)) + get_pub_key(name)
