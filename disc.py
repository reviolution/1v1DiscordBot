import discord
import asyncio
import elo

client = discord.Client()

ADMIN = 139354514091147264
PREFIX = '}'
DELETIONWAITTIME = 5


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    if message.content == ('<@' + str(client.user.id) + '>'):
        await sendMessage(message.channel, 'Current prefix is "' + PREFIX + '"')
        return
    if (message.content.startswith(PREFIX)) & (message.author.id != client.user.id):
        message.content = message.content[len(PREFIX):]
        args = message.content.split()
        if args[0] == 'help':
            tmpembed = discord.Embed(title='title', color=0xff0000, description='description').set_author(name='auhorname').set_footer(text='footertext').add_field(name='fieldname', value='fieldvalue').add_field(name='fieldname', value='fieldvalue')
            await message.channel.send('teeest', embed=tmpembed)



async def sendMessage(channel, messageText):
    await channel.trigger_typing()
    return await channel.send(messageText)


open('token.txt', 'a').close()
with open('token.txt', 'r') as tokenfile:
    token = tokenfile.readline()
client.run(token)
