#! /usr/bin/python

import account_manager as am
import node_pb2 as np

import translator

VERSION = 0


def tip(emitter, receiver, amount, grpc_stub):
    nb_esc = am.get_balance(emitter)
    if amount < nb_esc:
        return False
    raw_tx = prepare_tx(emitter, receiver, amount)
    grpc_stub.PublishRawTx(np.PublishRawTxRequest(raw_tx=raw_tx))
    return True


def prepare_tx(emitter, receiver, amount):


    op = np.Outpoint(hash="han", index=0)
    tx_in = np.TxInput(previous_output=op, script="honk")
    tx_out= np.TxOutput(value = amount, script="mouimouimoui")
    tx = np.Tx(version=0, flags=[],)

    nb_esc = am.get_balance(emitter)

    version = VERSION

    flags_count = 0  # a retraiter aux bons types avec le codec d'ensicoin-python
    flags = []

    inputs = am.get_tx_in(emitter)
    inputs_count = len(inputs)

    if amount == nb_esc:
        gift = am.make_tx_out(receiver, amount)
        outputs = [gift]

        am.reset_tx_in(emitter)
        am.add_tx_in(receiver, gift)

    else:
        stock = am.make_tx_out(emitter, nb_esc-amount)
        gift = am.make_tx_out(receiver, amount)
        outputs = [gift, stock]

        am.reset_tx_in(emitter)
        am.add_tx_in(emitter, stock)
        am.add_tx_in(receiver, gift)

    tx.create(version, flags_count, flags, inputs_count, inputs, outputs_count, outputs)

    return tx.encode()
