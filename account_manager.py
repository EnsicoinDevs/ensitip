#! /usr/bin/python
import json
import translator


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


    return translator.Var_array(liste_de_tx_in)


def make_tx_out(receiver, amount):
    tx_out = translator.Tx_out()

    pub_key = get_pub_key(receiver)

    script = chr(0x64) + chr(0xa0) + hash160(pub_key) + chr(0x78) + chr(0x8c) + chr(0xaa)
    #         OP_DUP    OP_HASH160 <hash160(pubKey)> OP_EQUAL OP_VERIFY OP_CHECKSIG

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
    comptes = json.dumps(f)["comptes"]
    f.close()



    new_tx_in = {}

    new_tx_in["hash"] = hash(tx)
    new_tx_in["index"] = 0
    new_tx_in["script"] = sign(tx, get_priv_key(name)) + get_pub_key(name)
