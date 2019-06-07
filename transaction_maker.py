#! /usr/bin/python

import account_manager as am



VERSION = 0


def tip(emitter, receiver, amount):
    nb_esc = get_balance(emitter)
    if amount < nb_esc:
        return False
    tx = prepare_tx(emitter, receiver, amount)
    #TODO: envoyer la tx a un noeud
    return True


def prepare_tx(emitter, receiver, amount):
    nb_esc = get_balance(emitter)

    version = VERSION
    flags_count = 0  #a retraiter aux bons types avec le codec d'ensicoin-python
    flags = 0
    inputs_count = 1
    inputs = [get_tx_in(emitter)]

    if amount == nb_esc:
        outputs_count = 1
        outputs = [make_tx_out(receiver, amount)]
        emitter.set_tx_in(None)
    else:
        outputs_count = 2
        stock = make_tx_out(emitter, nb_esc-amount)
        outputs = [make_tx_out(receiver, amount), stock]
        emitter.set_tx_in(stock)

    return tx_encode(version, flags_count, flags, inputs_count, inputs, outputs_count, outputs)


def tx_encode(version, flags_count, flags, inputs_count, inputs, outputs_count, outputs):
    # TODO avec le codec ensicoin python
    return "olala"
