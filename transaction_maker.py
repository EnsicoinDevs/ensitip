#! /usr/bin/python

import account_manager as am
import node_pb2

VERSION = 0


def int_to_bytes(x: int) -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')


def convert_to_varuint(uint):
    if uint <= 252:
        return uint
    if uint <= 0xFFFF:
        return (0xFD << 8*2) | uint
    if uint <= 0xFFFFFFFF:
        return (0xFE << 8*4) | uint
    if uint > 0xFFFFFFFFFFFFFFFF:
        return 0xFFFFFFFFFFFFFFFFFF
    return (0xFF << 8*8) | uint


class TxIn:
    def __init__(self, previous_hash, previous_index, script):
        self.previous_hash = previous_hash
        self.previous_index = previous_index
        self.script = script

    def bytes(self):
        return bytes(self.previous_hash) +\
               int_to_bytes(self.previous_index) +\
               int_to_bytes(convert_to_varuint(len(self.script))) +\
               bytes(self.script)


class TxOut:
    def __init__(self, value, script):
        self.value = value
        self.script = script

    def bytes(self):
        return self.value.to_bytes(4, byteorder='big') +\
               int_to_bytes(convert_to_varuint(len(self.script))) +\
               bytes(self.script)


class Tx:
    def __init__(self, version, flags, inputs, outputs):
        self.version = version
        self.flags = flags
        self.inputs = inputs
        self.outputs = outputs

    def bytes(self):
        # TODO
        return b"AH"


def tip(emitter, receiver, amount, grpc_stub):
    nb_esc = am.get_balance(emitter)
    if amount < nb_esc:
        return False
    raw_tx = prepare_tx(emitter, receiver, amount)
    grpc_stub.PublishRawTx(node_pb2.PublishRawTxRequest(raw_tx=raw_tx))
    return True


def prepare_tx(emitter, receiver, amount):
    nb_esc = am.get_balance(emitter)

    version = VERSION
    flags_count = 0  # a retraiter aux bons types avec le codec d'ensicoin-python
    flags = []
    inputs = [am.get_tx_in(emitter)]

    if amount == nb_esc:
        outputs = [am.make_tx_out(receiver, amount)]
        emitter.set_tx_in(None)
    else:
        stock = am.make_tx_out(emitter, nb_esc-amount)
        outputs = [am.make_tx_out(receiver, amount), stock]
        emitter.set_tx_in(stock)

    return Tx(version, flags, inputs, outputs).bytes()


def tx_encode(version,
              flags_count,
              flags,
              inputs_count,
              inputs,
              outputs_count,
              outputs):
    return "olala"
