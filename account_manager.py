#! /usr/bin/python
import json



def get_accounts():
    f = open("comptes.json","r")
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
    #a retraiter aux bons types avec le codec d'ensicoin-python
    raw = get_accounts()[name]["tx_in"]
    thash = raw["hash"]
    index = raw["index"]
    script = raw["script"]
    return thash + index + str(len(script)) + script # a raffiner grandement

def set_tx_in(name, tx):
    new_tx_in = {}

    new_tx_in["hash"] = hash(tx);
    new_tx_in["index"] = 0;
    new_tx_in["script"] = sign(tx, get_priv_key(name) ) + get_pub_key(name)

def sign(tx, key):
    # TODO:
    return "olali"
