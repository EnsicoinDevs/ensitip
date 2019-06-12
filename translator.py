#! /usr/bin/python

"""
copié collé d'une partie du codec d'ensicoin-python
"""


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

#-------------------------------------------------------------------------------

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

            if item_type == "tx_in":
                item = Tx_in()
                code = item.decode(code)
            if item_type == "tx_out":
                item = Tx_out()
                code = item.decode(code)
            if item_type == "str":
                item = Var_str()
                code = item.decode(code)

            values.append(item)

        self.__init__(values)
        return code

#-------------------------------------------------------------------------------

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

    def __init__(self, previous_output=Outpoint(), script=Var_str()):

        self.previous_output = previous_output
        #self.script_length = script_length   <-- incorporé dans le var_str
        self.script = script


    def __str__(self):
        output = "tx_in:\n"
        output +="  previous_output: " + str(self.previous_output) + "\n"
        output +="  script: " + str(self.script) + "\n"
        return output


    def encode(self):
        return self.previous_output.encode() + self.script.encode()


    def decode(self,code):
        previous_output = Outpoint()
        script = Var_str()

        code = previous_output.decode(code)
        code = script.decode(code)

        self.__init__(previous_output, script)
        return code


    def create(self, previous_output=Outpoint(), script=""):

        self.previous_output = previous_output
        self.script = Var_str(script)



class Tx_out:

    def __init__(self, value=Uint64(), script=Var_str()):

        self.value = value
        self.script = script


    def __str__(self):
        output = "tx_out:\n"
        output +="  value: " + str(self.value) + "\n"
        output +="  script: " + str(self.script) + "\n"
        return output


    def encode(self):
        return self.previous_output.encode() + self.script.encode()


    def decode(self,code):
        value = Uint64()
        script = Var_str()

        code = value.decode(code)
        code = script.decode(code)

        self.__init__(value, script)
        return code


    def create(self, value=0, script=""):

        self.value = Uint64(value)
        self.script = Var_str(script)
