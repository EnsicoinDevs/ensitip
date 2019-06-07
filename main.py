#! /usr/bin/python
import discord
import json

TOKEN = 'NDczMTM5NjgwOTI2MjM2Njc0.XPqSzg.oyeh9B6doL8IjYAaCaskeXhLeck'

client = discord.Client()

@client.event
async def on_message(message):
    print(message.author);
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content=='ensitip':
        msg = "utilisez 'ensitip aide' pour obtenir la liste des commandes utilisables"
        await message.channel.send(msg)

    if message.content[0:7]=='ensitip ':

        #msg = 'Salut, {0.author.mention}'.format(message)
        options = message.content[7:]

        if options.startswith("aide "):
            arg = options[5:]
            if arg.startswith("tip"):
                await message.channel.send("usage: ensitip tip <destinataire> <x>")
                await message.channel.send("envoie x ensicoins au destinataire")
                await message.channel.send("le destinataire est une mention discord")
                await message.channel.send("par exemple: 'ensipy tip @xX_rolandgrozdu122_Xx 27'")
                await message.channel.send("enverrait 27 ensicoins a l'utilisateur @xX_rolandgrozdu22_Xx")
            if arg.startswith("coin"):
                await message.channel.send("usage: ensitip coin")
                await message.channel.send("coin")
            if arg.startswith("voir"):
                await message.channel.send("usage: ensitip voir\n")
                await message.channel.send("renvoie la clef publique de votre wallet ensipy ainsi que le nombre d'ensicoins qu'il contient\n")
                await message.channel.send("c'est utile pour y déposer des ensicoins avec votre vraie clef privée, ou verifier combien on peut se permettre de tipper\n")

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
            f = open("comptes.json","r")
            data = f.read()
            f.close()

            comptes = json.load(data)["comptes"]
            nom = message.author

            if nom not in comptes:
                await message.channel.send("vous n'avez malheureusement pas encore de compte ensitip")
            else:
                await message.channel.send("nom:")

        else:
            await message.channel.send("utilisez 'ensitip aide' pour obtenir la liste des commandes utilisables")




@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)
