#! /usr/bin/python

import account_manager as am
import node_pb2

import translator

VERSION = 0


def tip(emitter, receiver, amount, grpc_stub):
    nb_esc = am.get_balance(emitter)
    if amount < nb_esc:
        return False
    raw_tx = prepare_tx(emitter, receiver, amount)
    grpc_stub.PublishRawTx(node_pb2.PublishRawTxRequest(raw_tx=raw_tx))
    return True


def prepare_tx(emitter, receiver, amount):

    tx = translator.Transaction()

    nb_esc = am.get_balance(emitter)

    version = VERSION

    flags_count = 0  # a retraiter aux bons types avec le codec d'ensicoin-python
    flags = []

    inputs = am.get_tx_in(emitter)
    inputs_count = len(inputs)

    if amount == nb_esc:
        outputs = [am.make_tx_out(receiver, amount)]
        emitter.set_tx_in(None)
    else:
        stock = am.make_tx_out(emitter, nb_esc-amount)
        outputs = [am.make_tx_out(receiver, amount), stock]
        emitter.set_tx_in(stock)

    tx.create(version, flags_count, flags, inputs_count, inputs, outputs_count, outputs)

    return tx.encode()
