#! /usr/bin/python
import discord
import json
import grpc

import account_manager as am
import transaction_maker as tm
import node_pb2_grpc as npg
import node_pb2 as np

TOKEN = 'NDczMTM5NjgwOTI2MjM2Njc0.XPqSzg.oyeh9B6doL8IjYAaCaskeXhLeck'

client = discord.Client()
channel = grpc.insecure_channel("localhost:4225")
stub = npg.NodeStub(channel)

addr = np.Address(ip = "78.248.188.120", port= 4224)
pair = np.Peer(address = addr)

stub.ConnectPeer(np.ConnectPeerRequest(peer = pair))
stub.GetBestBlocks(np.GetBestBlocksRequest())


@client.event
async def on_message(message):
    global client

    if message.author == client.user: #message.author == bot: would replie to himself
        return



    if message.content.lower() == 'ensitip':
        print(str(message.author) + " : " + str(message.content))
        msg = "utilisez 'ensitip aide' pour obtenir la liste des commandes utilisables"
        await message.channel.send(msg)



    if message.content[0:8].lower() == 'ensitip ':
        print(str(message.author) + " : " + str(message.content))
        # msg = 'Salut, {0.author.mention}'.format(message)
        options = message.content[8:]

        if options.startswith("aide "):
            arg = options[5:]
            if arg.startswith("tip"):
                await message.channel.send('usage: ensitip tip <destinataire> <x>')
                await message.channel.send("envoie x ensicoins au destinataire")
                await message.channel.send("le destinataire est une mention discord")
                await message.channel.send('par exemple:  ensitip tip @xX_rolandgrozdu35_Xx 27')
                await message.channel.send("enverrait 27 ensicoins a l'utilisateur @xX_rolandgrozdu35_Xx")
            if arg.startswith("coin"):
                await message.channel.send("usage: ensitip coin")
                await message.channel.send("coin")
            if arg.startswith("voir"):
                await message.channel.send("usage: ensitip voir\n")
                await message.channel.send("envoie en MP les clefs de votre wallet ensipy ainsi que le nombre d'ensicoins qu'il contient\n")
                await message.channel.send("c'est utile pour y déposer des ensicoins avec votre vraie clef privée, ou verifier combien on peut se permettre de tipper\n")
            if arg.startswith("cree"):
                await message.channel.send("usage: ensitip cree")
                await message.channel.send("cree une paire de clef ensicoin et un compte ensitip lié a votre nom discord.")
                await message.channel.send("(n'oubliez pas de recuperer vos ensicoins avant de changer de nom discord)")



        elif options.startswith("aide"):
            await message.channel.send("liste des commandes légales:")
            await message.channel.send("|   tip")
            await message.channel.send("|   coin")
            await message.channel.send("|   voir")
            await message.channel.send("|   cree")
            await message.channel.send("utilisez 'ensitip aide <commande>' pour recevoir plus d'informations sur son usage")



        elif options.startswith("coin"):
            await message.channel.send("coin")



        elif options.startswith("voir"):
            f = open("comptes.json", "r")
            comptes = json.load(f)["comptes"]
            f.close()

            auth = message.author
            nom = str(auth.id)
            chan = auth.dm_channel
            if chan is None:
                await auth.create_dm()
                chan = auth.dm_channel

            if nom not in comptes:
                await message.channel.send("vous n'avez malheureusement pas encore de compte ensitip")
            else:
                await chan.send("clef publique: {}".format(comptes[nom]["clef_pub"]))
                await chan.send("clef privée: {}".format(comptes[nom]["clef_priv"]))



        elif options.startswith("cree"):
            msg = am.create_new_account(message.author.id)
            await message.channel.send(msg)



        elif options.startswith("tip"):
            auth = message.author
            emitter = str(auth.id)

            donnees = options[4:]
            if len(donnees) != 0:

                if donnees[0] == " ": #pour les utilisateurs de mobiles
                    donnees = donnees[1:]

                if donnees.startswith('<@'):
                    destinataire = ""
                    i = 2

                    if donnees[i] == "!": #pour les utilisateurs PC
                        i=i+1

                    while i<len(donnees) and donnees[i] != '>':
                        destinataire = destinataire + str(donnees[i])
                        i+=1

                    if i > len(donnees):
                        await message.channel.send("vous êtes un petit rigolo qui a mis un '<' avant un destinataire mal formaté pour essayer de me tromper è_é")

                    elif i+1 > len(donnees):
                        await message.channel.send("vous avez oublié le montant")

                    else:
                        num = donnees[i+1:]
                        test_num =False
                        test_nom =False
                        try:
                            num = int(num)
                            test_num = True
                        except:
                            await message.channel.send("le montant n'est pas un entier è_é")

                        try:
                            destinataire = int(destinataire)
                            test_nom = True
                        except:
                            await message.channel.send("l'id du destinataire n'est pas un entier è_é")

                        if test_num and test_nom:

                            await message.channel.send("tentative de transaction :3")

                            tip(emitter, destinataire, num, stub)

                else:
                    await message.channel.send("avez-vous bien *mentionné* le destinataire ?")

            else:
                await message.channel.send("vous avez oublié le destinataire")



        else:
            await message.channel.send("utilisez 'ensitip aide' pour obtenir la liste des commandes utilisables")


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)
