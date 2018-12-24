import discord
import logging
import asyncio
import elo

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

ADMIN = 139354514091147264
DELETIONWAITTIME = 5
COMPUTINGEMBED = discord.Embed(title='Computing match')

class Client(discord.Client):
    async def on_ready(self):
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('------')

    async def on_message(self, message):
        if message.author == client.user:
            return
        if message.content.startswith('<@' + str(client.user.id) + '>'):
            message.content = message.content[len('<@' + str(client.user.id) + '>'):]
            args = message.content.split()
            if len(args) == 0:
                await sendMessage(message.channel, 'Current prefix is "<@' + str(client.user.id) + '>"')
            elif args[0].lower() == 'challenge':
                if (len(message.mentions) != 2) | (len(args) != 2):
                    await sendAndDeleteMessage(message.channel, 'Falsches Befehlsformat! Nutze: "' + '<@' + str(
                        client.user.id) + '>' + ' challenge @Gegner' + '"')
                elif (len(message.mentions) == 2) & (len(args) == 2):
                    challenger = message.author
                    for mention in message.mentions:
                        if mention.id != client.user.id:
                            challenged = mention
                    if challenged == challenger:
                        await sendAndDeleteMessage(message.channel, 'Du Spast kannst dich nicht selbst herausfordern')
                        return
                    tmpembed = discord.Embed(title='**League of Legends 1vs1 Match**',
                                             url='https://www.youtube.com/watch?v=ftBrkM4JueI')
                    tmpembed.colour = discord.Colour(0xff0000)
                    tmpembed.set_footer(text=str(challenger.id) + ' ' + str(challenged.id))
                    if elo.getMatchCount(challenger.id) < elo.placementMatches:
                        tmpembed.add_field(name=challenger.name,
                                           value=str(elo.getMatchCount(challenger.id)) + '/' + str(
                                               elo.placementMatches) + ' Placements', inline=True)
                    else:
                        tmpembed.add_field(name=challenger.name, value=str(elo.getUserElo(challenger.id)) + ' MMR',
                                           inline=True)
                    if elo.getMatchCount(challenged.id) < elo.placementMatches:
                        tmpembed.add_field(name=challenged.name,
                                           value=str(elo.getMatchCount(challenged.id)) + '/' + str(
                                               elo.placementMatches) + ' Placements', inline=True)
                    else:
                        tmpembed.add_field(name=challenged.name, value=str(elo.getUserElo(challenged.id)) + ' MMR',
                                           inline=True)
                    msg = await message.channel.send(embed=tmpembed)
                    await msg.add_reaction('⬅')
                    await msg.add_reaction('➡')
                    await msg.add_reaction('❌')
                    return

    async def on_reaction_add(self, reaction, user):
        if user == client.user:
            return
        message = reaction.message
        if (message.content == '') & (len(message.embeds) == 1) & (message.author == client.user):
            footer = message.embeds[0].footer.text
            if (reaction.emoji == '❌') & (str(user.id) in footer.split()):
                await message.delete()
                return
            if reaction.emoji == '⬅':
                count = 0
                async for reactuser in reaction.users():
                    if str(reactuser.id) in footer.split():
                        count = count + 1
                if count == 2:
                    await message.edit(embed=COMPUTINGEMBED)
                    p1 = footer.split()[0]
                    p2 = footer.split()[1]
                    await computeGame(p1, p2, True, message)
                return
            elif reaction.emoji == '➡':
                count = 0
                async for reactuser in reaction.users():
                    if str(reactuser.id) in footer.split():
                        count = count + 1
                if count == 2:
                    await message.edit(embed=COMPUTINGEMBED)
                    p1 = footer.split()[0]
                    p2 = footer.split()[1]
                    await computeGame(p1, p2, False, message)
                return



async def sendMessage(channel, messageText):
    await channel.trigger_typing()
    return await channel.send(messageText)


async def sendAndDeleteMessage(channel, messageText):
    tmpmessage = await sendMessage(channel, messageText)
    await asyncio.sleep(DELETIONWAITTIME)
    await tmpmessage.delete()


async def computeGame(p1, p2, p1win, message):
    p1old = elo.getUserElo(p1)
    p2old = elo.getUserElo(p2)
    challenger = message.guild.get_member(int(p1))
    challenged = message.guild.get_member(int(p2))
    elo.computeGame(p1, p2, p1win)
    p1diff = elo.getUserElo(p1) - p1old
    p2diff = elo.getUserElo(p2) - p2old
    if p1win:
        tmpembed = discord.Embed(title='**' + challenger.name + ' wins!**',
                                 url='https://www.youtube.com/watch?v=ftBrkM4JueI')
    else:
        tmpembed = discord.Embed(title='**' + challenged.name + ' wins!**',
                                 url='https://www.youtube.com/watch?v=ftBrkM4JueI')
    tmpembed.colour = discord.Colour(0xff0000)
    tmpembed.set_footer(text=str(challenger.id) + ' ' + str(challenged.id))

    if elo.getMatchCount(p1) < elo.placementMatches:
        tmpembed.add_field(name=challenger.name,
                           value=str(elo.getMatchCount(p1)) + '/' + str(elo.placementMatches) + ' Placements',
                           inline=True)
    else:
        tmpembed.add_field(name=challenger.name,
                           value=str(elo.getUserElo(p1)) + ' MMR (' + str(p1diff) + ')', inline=True)

    if elo.getMatchCount(p2) < elo.placementMatches:
        tmpembed.add_field(name=challenged.name,
                           value=str(elo.getMatchCount(p2)) + '/' + str(elo.placementMatches) + ' Placements',
                           inline=True)
    else:
        tmpembed.add_field(name=challenged.name,
                           value=str(elo.getUserElo(p2)) + ' MMR (' + str(p2diff) + ')', inline=True)

    await message.edit(embed=tmpembed)
    await message.clear_reactions()


open('token.txt', 'a').close()
with open('token.txt', 'r') as tokenfile:
    token = tokenfile.readline()
client = Client()
client.run(token)
