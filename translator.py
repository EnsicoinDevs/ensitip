#! /usr/bin/python

"""
copié collé du codec d'ensicoin-python
overkill pour l'usage qu'on en a ici
"""

VERSION = 0
MAGIC = 422021

SERVICE_COUNT = 0
SERVICES = []


def iter_bytes(n):
    hexa = hex(n)[2:]
    if len(hexa)%2 == 1:
        hexa = "0"+hexa
    while hexa != "":
        yield int(("0x" + hexa[0:2]),16)
        hexa = hexa[2:]


def encode_number(n,longueur):
    witch = ""
    for byte in iter_bytes(n):
        witch += chr(byte)
    return chr(0x00)*(int(longueur)-len(witch)) + witch


def decode_number(encoded_n):
    i=len(encoded_n)-1
    n=0
    for c in encoded_n:
        k = ord(c)
        n += (256**i)*k
        i-=1
    return n


def encode_string(s,longueur):
    return s + chr(0x00)*(int(longueur)-len(s))


def decode_string(encoded_s): #attention: conserve les zeros
    s = ""
    for c in encoded_s:
        #if c != chr(0):
        s+=c
    return s



def decode_message(code):
    magic = code[0:4]
    m_type = code[4:16]
    m_length = code[16:24]
    payload = code[24:]

    return (decode_number(magic),
            decode_string(m_type),
            decode_number(m_length),
            decode_string(payload))


def decode_address(code):
    timestamp = code[0:8]
    ip = code[8:24]
    port = code[24:26]

    return (decode_number(timestamp),
            decode_string(ip),
            decode_number(port))


class Uint16:

    def __init__(self, value=0):
        self.value = int(value)

    def __str__(self):
        return str(self.value)

    def __int__(self):
        return self.value

    def encode(self):
        return encode_number(self.value,2)

    def decode(self, code):
        cut = 2
        value = decode_number(code[:cut])
        self.__init__(value)
        return code[cut:]


class Uint32:

    def __init__(self, value=0):
        self.value = int(value)

    def __str__(self):
        return str(self.value)

    def __int__(self):
        return self.value

    def encode(self):
        return encode_number(self.value,4)

    def decode(self, code):
        cut = 4
        value = decode_number(code[:cut])
        self.__init__(value)
        return code[cut:]



class Uint64:

    def __init__(self, value=0):
        self.value = int(value)

    def __str__(self):
        return str(self.value)

    def __int__(self):
        return self.value

    def encode(self):
        return encode_number(self.value,8)

    def decode(self, code):
        cut = 8
        value = decode_number(code[:cut])
        self.__init__(value)
        return code[cut:]



class Var_uint:

    def __init__(self, value=0):
        self.value = int(value)

        if 0 <= int(value) <= 0xFF:
            self.length = 8

        elif 0x100 <= int(value) <= 0xFFFF:
            self.length = 16

        elif 0x10000 <= int(value) <= 0xFFFFFFFF:
            self.length = 32

        elif 0x100000000 <= int(value) <= 0xFFFFFFFFFFFFFFFF:
            self.length = 64


    def __str__(self):
        return str(self.value)

    def __int__(self):
        return self.value

    def encode(self):
        if self.length == 8:
            return encode_number(self.value,self.length//4-1)
        dico = {16:chr(0xFD), 32:chr(0xFE), 64:chr(0xFF)}
        return dico[self.length] + encode_number(self.value,self.length//4-1)

    def decode(self, code):
        var_type = code[0]

        cut = 0
        if var_type == chr(0xFF):
            cut = 8
            code = code[1:]  #the indicator is removed

        elif var_type == chr(0xFE):
            cut = 4
            code = code[1:]

        elif var_type == chr(0xFD):
            cut = 2
            code = code[1:]

        else:
            cut = 1

        value = decode_number(code[:cut])
        self.__init__(value)
        return code[cut:]



class Finite_str:

    def __init__(self, value="", length=0):
        self.value = str(value)
        self.length = Var_uint(length)

    def __str__(self):
        return str(self.value)

    def encode(self):
        return encode_string(self.value, self.length)

    def decode(self, code, length):
        cut=int(length)
        value = decode_string(code[:cut])

        self.__init__(value,length)
        return code[cut:]



class Var_str():
    def __init__(self, value=""):

        self.length = Var_uint(len(value))
        self.value = Finite_str(value, self.length)

    def __str__(self):
        return str(self.value)

    def encode(self):
        return self.length.encode() + encode_string(str(self.value), self.length)

    def decode(self, code):
        length = Var_uint()

        code = length.decode(code)
        cut=int(length)
        value = decode_string(code[:cut])
        self.__init__(value)
        return code[cut:]



class Var_array():
    def __init__(self, values=[]):

        self.length = Var_uint(len(values))
        self.values = values

    def __str__(self):
        return str(list(str(e) for e in self.values))

    def encode(self):
        code = ""
        for value in self.values:
            code += value.encode()
        return self.length.encode() + code

    def decode(self, code, item_type):
        values = []
        length = Var_uint()

        code = length.decode(code)

        for i in range(int(length)):
            item = None

            if item_type == "address":
                item = Address()
                code = item.decode(code)
            if item_type == "inventory":
                item = Inv_vect()
                code = item.decode(code)
            if item_type == "flag":
                item = Var_str()
                code = item.decode(code)
            if item_type == "transaction":
                item = Transaction()
                code = item.decode(code)
            if item_type == "tx_in":
                item = Tx_in()
                code = item.decode(code)
            if item_type == "tx_out":
                item = Tx_out()
                code = item.decode(code)
            if item_type == "block":
                item = Block()
                code = item.decode(code)
            if item_type == "str":
                item = Var_str()
                code = item.decode(code)

            values.append(item)

        self.__init__(values)
        return code



class Message:

    def __init__(self, p_type=Finite_str(), p_length=Uint64(), payload=Finite_str(), magic=Uint32()):
        self.magic = magic
        self.type = Finite_str(str(p_type), 12)
        self.length = p_length
        self.payload = Finite_str(str(payload), self.length)


    def __str__(self):
        output = "message:\n"
        output +="  magic number: " + str(self.magic) + "\n"
        output +="  type: " + str(self.type) + "\n"
        output +="  length: " + str(self.length) + "\n"
        output +="  payload: " + str(self.payload) + "\n"
        return output


    def encode(self):
        return self.magic.encode() + self.type.encode() + self.length.encode() + self.payload.encode()


    def decode(self,code):
        magic = Uint32()
        p_type = Finite_str()
        p_length = Uint64()
        payload = Finite_str()

        code = magic.decode(code)
        code = p_type.decode(code, 12)
        code = p_length.decode(code)
        code = payload.decode(code, p_length)

        self.__init__(p_type, p_length, payload, magic)
        return code


    def create(self, p_type="whoamiack", p_length=0, payload="", magic=MAGIC):
        self.magic = Uint32(magic)
        self.type = Finite_str(p_type, 12)
        self.length = Uint64(p_length)
        self.payload = Finite_str(payload, self.length)


class Address:

    def __init__(self, timestamp=Uint64(), ip=Finite_str(), port=Uint16()):
        self.timestamp = timestamp
        self.ip = ip
        self.port = port


    def __str__(self):
        output = "address:\n"
        output +="  timestamp: " + str(self.timestamp) + "\n"
        output +="  ip: " + str(self.ip) + " port:" + str(self.port) + "\n"
        return output


    def encode(self):
        return self.timestamp.encode() + self.ip.encode() + self.port.encode()


    def decode(self,code):
        timestamp = Uint64()
        ip = Finite_str()
        port = Uint16()

        code = timestamp.decode(code)
        code = ip.decode(code, 16)
        code = port.decode(code)

        self.__init__(timestamp, ip, port)
        return code


    def create(self, timestamp=1554580786, ip=chr(0)*10 + chr(255)*2 + chr(127) + chr(0) + chr(0) + chr (1), port=4224):
        self.timestamp = Uint64(timestamp)
        self.ip = Finite_str(ip, 16)
        self.port = Uint16(port)



class Inv_vect:

    def __init__(self, o_type=Uint32(), o_hash=Finite_str()):
        self.type = o_type
        self.hash = o_hash


    def __str__(self):
        output = "inv_vect:\n"
        output +="  type: " + str(self.type) + "\n"
        output +="  hash: " + str(self.hash) + "\n"
        return output


    def encode(self):
        return self.type.encode() + self.hash.encode()


    def decode(self,code):
        o_type = Uint32()
        o_hash = Finite_str()

        code = o_type.decode(code)
        code = o_hash.decode(code, 32)

        self.__init__(o_type, o_hash)
        return code


    def create(self, o_type="", o_hash=""):
        self.type = Uint32(o_type)
        self.hash = Finite_str(o_hash,32)



class Whoami:

    def __init__(self, version=Uint32(), emetteur=Address(),
                 service_count=Var_uint(), services=Var_array()):
        self.version = version
        self.emetteur = emetteur
        self.service_count = service_count
        self.services = services


    def __str__(self):
        output = "whoami:\n"
        output +="  version: " + str(self.version) + "\n"
        output +="  emetteur: " + str(self.emetteur) + "\n"
        output +="  service_count: " + str(self.service_count) + "\n"
        output +="  services: " + str(self.services) + "\n"
        return output


    def encode(self):
        return self.version.encode() + self.emetteur.encode() + self.services.encode()


    def decode(self,code):
        version = Uint32()
        emetteur = Address()
        #service_count=Var_uint()
        services=Var_array()

        code = version.decode(code)
        code = emetteur.decode(code)
        #code = service_count.decode(code)
        code = services.decode(code, "str")

        service_count = Var_uint(services.length)

        self.__init__(version, emetteur, service_count, services)
        return code


    def create(self, version=0, emetteur=Address(), services_count=0, services=[]):
        self.version = Uint32(version)
        self.emetteur = emetteur
        self.service_count = Var_uint(services_count)
        self.services = Var_array(services)




class Addr:

    def __init__(self, count=Var_uint(), addresses=Var_array()):
        self.count = count
        self.addresses = addresses


    def __str__(self):
        output = "addr:\n"
        output +="  count: " + str(self.count) + "\n"
        output +="  addresses: " + str(self.addresses) + "\n"
        return output


    def encode(self):
        return self.count.encode() + self.addresses.encode()


    def decode(self,code):
        count = Uint32()
        addresses = Var_array()

        code = count.decode(code)
        code = addresses.decode(code, "address")

        self.__init__(count, addresses)
        return code


    def create(self, count=0, addresses=[]):
        self.count = Var_uint(count)
        self.addresses = Var_array(addresses)


class Inv:

    def __init__(self, count=Var_uint(), inventory=Var_array()):
        self.count = count
        self.inventory = inventory


    def __str__(self):
        output = "inv:\n"
        output +="  count: " + str(self.count) + "\n"
        output +="  inventory: " + str(self.inventory) + "\n"
        return output


    def encode(self):
        return self.count.encode() + self.inventory.encode()


    def decode(self,code):
        count = Uint32()
        inventory = Var_array()

        code = count.decode(code)
        code = inventory.decode(code, "inventory")

        self.__init__(count, inventory)
        return code


    def create(self, count=0, inventory=[]):
        self.count = Var_uint(count)
        self.inventory = Var_array(inventory)



class Block:

    def __init__(self, version=Uint32(), flags_count=Var_uint(), flags=Var_array(),
                 prev_block=Finite_str(), merkle_root=Finite_str(), timestamp=Uint64(),
                 height=Uint32(), bits=Uint32(), nonce=Uint64(),
                 transactions_count=Var_uint(), transactions=Var_array()):

        self.version = version
        self.flags_count = flags_count
        self.flags = flags
        self.prev_block = prev_block
        self.merkle_root = merkle_root
        self.timestamp = timestamp
        self.height = height
        self.bits = bits
        self.nonce = nonce
        self.transactions_count = transactions_count
        self.transactions = transactions


    def __str__(self):
        output = "block:\n"
        output +="  version: " + str(self.version) + "\n"
        output +="  prev_block: " + str(self.prev_block) + "\n"
        output +="  height: " + str(self.height) + "\n"
        return output


    def encode(self):

        debut = self.version.encode() + self.flags_count.encode() + self.flags.encode()
        milieu1 = self.prev_block.encode() + self.merkle_root.encode() + self.timestamp.encode()
        milieu2 = self.height.encode() + self.bits.encode() + self.nonce.encode()
        fin = self.transactions_count.encode() + self.transactions.encode()

        return debut + milieu1 + milieu2 + fin


    def decode(self,code):
        version = Uint32()
        flags_count = Var_uint()
        flags = Var_array()
        prev_block = Finite_str()
        merkle_root = Finite_str()
        timestamp = Uint64()
        height = Uint32()
        bits = Uint32()
        nonce = Uint64()
        transactions_count = Var_uint()
        transactions = Var_array()

        code = version.decode(code)
        code = flags_count.decode(code)
        code = flags.decode(code, "flag")
        code = prev_block.decode(code, 32)
        code = merkle_root.decode(code, 32)
        code = timestamp.decode(code)
        code = height.decode(code)
        code = bits.decode(code)
        code = nonce.decode(code)
        code = transactions_count.decode(code)
        code = transactions.decode(code, "transaction")

        self.__init__(version, flags_count, flags, prev_block,
                      merkle_root, timestamp, height, bits, nonce,
                      transactions_count, transactions)
        return code


    def create(self, version=0, flags_count=0, flags=[], prev_block="",
                 merkle_root="", timestamp=0, height=0, bits=0, nonce=0,
                 transactions_count=0, transactions=[]):

        self.version = Uint32(version)
        self.flags_count = Var_uint(flags_count)
        self.flags = Var_array(flags)
        self.prev_block = Finite_str(prev_block, 32)
        self.merkle_root = Finite_str(merkle_root, 32)
        self.timestamp = Uint64(timestamp)
        self.height = Uint32(height)
        self.bits = Uint32(bits)
        self.nonce = Uint64(nonce)
        self.transactions_count = Var_uint(transactions_count)
        self.transactions = Var_array(transactions)



class Transaction:

    def __init__(self, version=Uint32(), flags_count=Var_uint(), flags=Var_array(), inputs_count=Var_uint(),
                 inputs=Var_array(), outputs_count=Var_uint(), outputs=Var_array()):

        self.version = version
        self.flags_count = flags_count
        self.flags = flags
        self.inputs_count = inputs_count
        self.inputs = inputs
        self.outputs_count = outputs_count
        self.outputs = outputs


    def __str__(self):
        output = "transaction:\n"
        output +="  version: " + str(self.version) + "\n"
        output +="  inputs: " + str(self.inputs) + "\n"
        output +="  outputs: " + str(self.outputs) + "\n"
        return output


    def encode(self):

        debut = self.version.encode() + self.flags_count.encode() + self.flags.encode()
        milieu = self.inputs_count.encode() + self.inputs.encode()
        fin = self.outputs_count.encode() + self.outputs.encode()

        return debut + milieu + fin


    def decode(self,code):
        version = Uint32()
        flags_count = Var_uint()
        flags = Var_array()
        inputs_count = Var_uint()
        inputs = Var_array()
        outputs_count = Var_uint()
        outputs = Var_array()

        code = version.decode(code)
        code = flags_count.decode(code)
        code = flags.decode(code, "flag")
        code = inputs_count.decode(code)
        code = inputs.decode(code, "tx_in")
        code = outputs_count.decode(code)
        code = outputs.decode(code, "tx_out")


        self.__init__(version, flags_count, flags, inputs_count,
                      inputs, outputs_count, outputs)
        return code


    def create(self, version=0, flags_count=0, flags=[], inputs_count=0,
               inputs=[], outputs_count=0, outputs=[]):

        self.version = Uint32(version)
        self.flags_count = Var_uint(flags_count)
        self.flags = Var_array(flags)
        self.inputs_count = Var_uint(inputs_count)
        self.inputs = Var_array(inputs)
        self.outputs_count = Var_uint(outputs_count)
        self.outputs = Var_array(outputs)



class Outpoint:

    def __init__(self, t_hash=Finite_str(), index=Uint32()):

        self.hash = t_hash
        self.index = index


    def __str__(self):
        output = "outpoint:\n"
        output +="  hash: " + str(self.hash) + "\n"
        output +="  index: " + str(self.index) + "\n"
        return output


    def encode(self):
        return self.hash.encode() + self.index.encode()


    def decode(self,code):
        t_hash = Finite_str()
        index = Uint32()

        code = t_hash.decode(code)
        code = index.decode(code, "inventory")

        self.__init__(t_hash, index)
        return code


    def create(self, t_hash="", index=0):

        self.hash = Finite_str(t_hash)
        self.index = Uint32(index)



class Tx_in:

    def __init__(self, previous_output=Outpoint(), script_length=Var_uint(), script=Var_array()):

        self.previous_output = previous_output
        self.script_length = script_length
        self.script = script


    def __str__(self):
        output = "tx_in:\n"
        output +="  previous_output: " + str(self.previous_output) + "\n"
        output +="  script_length: " + str(self.script_length) + "\n"
        output +="  script: " + str(self.script) + "\n"
        return output


    def encode(self):
        return self.previous_output.encode() + self.script_length.encode() + self.script.encode()


    def decode(self,code):
        previous_output = Outpoint()
        script_length = Var_uint()
        script = Var_array()

        code = previous_output.decode(code)
        code = script_length.decode(code)
        code = script.decode(code)

        self.__init__(previous_output, script_length, script)
        return code


    def create(self, previous_output=Outpoint(), script_length=0, script=""):

        self.previous_output = previous_output
        self.script_length = Var_uint(script_length)
        self.script = Var_array(script)



class Tx_out:

    def __init__(self, value=Uint64(), script_length=Var_uint(), script=Var_array()):

        self.value = value
        self.script_length = script_length
        self.script = script


    def __str__(self):
        output = "tx_out:\n"
        output +="  value: " + str(self.value) + "\n"
        output +="  script_length: " + str(self.script_length) + "\n"
        output +="  script: " + str(self.script) + "\n"
        return output


    def encode(self):
        return self.previous_output.encode() + self.script_length.encode() + self.script.encode()


    def decode(self,code):
        value = Uint64()
        script_length = Var_uint()
        script = Var_array()

        code = value.decode(code)
        code = script_length.decode(code)
        code = script.decode(code)

        self.__init__(value, script_length, script)
        return code


    def create(self, value=0, script_length=0, script=""):

        self.value = Uint64(value)
        self.script_length = Var_uint(script_length)
        self.script = Var_array(script)



class Getblocks():

    def __init__(self, count=Var_uint(), locator=Finite_str(), b_hash=Finite_str()):

        self.count = count
        self.locator = locator
        self.hash = b_hash


    def __str__(self):
        output = "getblocks:\n"
        output +="  count: " + str(self.count) + "\n"
        output +="  locator: " + str(self.locator) + "\n"
        output +="  hash: " + str(self.hash) + "\n"
        return output


    def decode(self,code):
        count = Var_uint()
        locator = Var_array()
        b_hash = Finite_str()

        code = count.decode(code)
        code = locator.decode(code)
        code = b_hash.decode(code,32)

        self.__init__(count, locator, b_hash)
        return code


    def encode(self):
        return self.count.encode() + self.locator.encode() + self.hash.encode()


    def create(self, count=0, locator=[], b_hash=""):

        self.count = Var_uint(count)
        self.locator = Var_array(locator)
        self.hash = Finite_str(b_hash, 32)




def global_decode(message):
    m = Message()
    m.decode(message)

    payload_type = str(m.type)
    payload = m.payload

    if payload_type == "whoami":
        decoded_payload = Whoami()
        decoded_payload.decode(payload)

    elif payload_type == "whoamiack":
        decoded_payload = None

    elif payload_type == "getaddr":
        decoded_payload = None

    elif payload_type == "addr":
        decoded_payload = Addr()
        decoded_payload.decode(payload)

    elif payload_type == "inv":
        decoded_payload = Inv()
        decoded_payload.decode(payload)

    elif payload_type == "getdata":
        decoded_payload = Inv()
        decoded_payload.decode(payload)

    elif payload_type == "notfound":
        decoded_payload = Inv()
        decoded_payload.decode(payload)

    elif payload_type == "block":
        decoded_payload = Block()
        decoded_payload.decode(payload)

    elif payload_type == "tx":
        decoded_payload = Transaction()
        decoded_payload.decode(payload)
        payload_type = "transaction"

    elif payload_type == "getblocks":
        decoded_payload = Inv()
        decoded_payload.decode(payload)

    elif payload_type == "getmempool":
        decoded_payload = None

    else:
        decoded_payload = None
        payload_type = "error"

    return int(message.magic), payload_type, int(message.length), decoded_payload


if __name__ == "__main__":

    a=Message()
    a.create("inv",8,"a")
    print(a.encode())
    b=Message()
    b.decode(a.encode())
    print(b)
