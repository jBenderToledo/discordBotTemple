import discord # currently using v1.0.0a
from discord.ext import commands
from time import strftime
from datetime import datetime
import asyncio
from itertools import cycle
import os

#
# @author Jonathan Bender
#

botname = "Cirno"
client = commands.Bot(command_prefix = '>>')
server_name = "Temple"

bot_version = "0.3" + " " + "alpha"
deleted_log_dir_name = "deleted/" + server_name + datetime.now().strftime("%Y")


# Change the following to match your target server
admin_id = 482655890537840660
admin_role = 'admin'

moderator_id = 482378769605328916
moderator_role = 'moderator'
# -----------------------------------------------

lack_credentials_fmt = 'You are not a(n) {}.'
local_statement_fmt = "<{0.author}> {0.content}"
statement_fmt = "[{0.channel}]" + local_statement_fmt

# This allows me to put my token in a separate file
# rather than putting it in my source code like I see
# a nonzero number of people doing. Yuck.

fo = open('{}.txt'.format("bot"), 'r')
TOKEN = fo.read()[0 : len(fo.read()) - 1]
fo.close()

# TODO learn how to throw exceptions
if len(TOKEN) != 59:
    print("ERROR: Token var is not a token!")
    exit()


# -----------------------
# - AUXILIARY FUNCTIONS -
# -----------------------

async def getTimeStr() -> str:
    return datetime.now().strftime('%m-%d, %H;%M')

async def getMonth() -> str:
    return datetime.now().strftime('%B')

# -----------------------
# -      FILE I/O       -
# -----------------------

#
# Void. Makes a subdirectory of the source code's root.
#
# @param path : path starting from execution folder. Use '/' for subdirectories.
#
def make_dir(path : str, delimiter : str):
    path_list = path.split(delimiter)

    # starting at 1 because lists are indexed at 0
    for index in range(1, len(path_list)):
        path_list[index] = path_list[index - 1] + delimiter + path_list[index]

    for folder in path_list:
        try:
            os.mkdir(folder)
            print(".{0}{1}{0} created.".format(delimiter, folder))
        except FileExistsError:
            pass

def append_file(path, name, data):
    """
    Appends onto the contents of ./path/name the contents
    of data.

    @param path : path starting from execution folder
    @param name : Filename and extension.
    @param data : Data to append onto the end of ./path/name
    """

    make_dir(path, '/')

    backup_file = open(
        "{}/{}".format(path, name), 'a'
    )

    print("{}/{} modified.".format(path, name))
    backup_file.write(data)
    backup_file.close()

# -----------------------
# -   BOT INTERRUPTS    -
# - @client.event       -
# -----------------------

@client.event
async def on_message(message):
    # add stuff when desired
    await client.process_commands(message)

# -----------------------
# -    BOT COMMANDS     -
# - @client.command()   -
# -----------------------

@client.command()
async def ping(message):
    await message.channel.send("pong!")

@client.command(pass_context = True)
async def del_msg(ctx, amount = 0, backup_is_enabled = True):
    channel = ctx.message.channel
    author = ctx.message.author
    message = ctx.message
    message_list = []
    test_list = []
    backup_str = ''
    time = await getTimeStr()

    backup_is_enabled = bool(backup_is_enabled)
    deleting_all = False

    if admin_id in [role.id for role in author.roles]:
        if amount < 0:
            await channel.send(
                "Go home, {}. You're drunk.".format(author.display_name)
            )
            return

        async for message in channel.history(limit = amount + 1):
            message_list.append(message)
        async for message in channel.history():
            test_list.append(message)


        if len(message_list) == len(test_list):
            deleting_all = True

        length = len(message_list)

        message_list.reverse()
        for message in message_list:
            print(local_statement_fmt.format(message))
            backup_str += local_statement_fmt.format(message) + '\n'
        backup_str += time + '\n'
        message_list.reverse()

        await channel.delete_messages(message_list)

        if deleting_all:
            await channel.send('All messages deleted in {}.'.format(channel))
            print("All messages deleted in {}.".format(channel))
        else:
            await channel.send(
                '{} messages deleted in #{}.'.format(length, channel))

        print("{} messages deleted in #{}.".format(length, channel))

        if backup_is_enabled and amount > 1:
            month = await getMonth()
            date = await getTimeStr()

            backup_dir = deleted_log_dir_name + "/" + month + "/" + str(channel)
            append_file(backup_dir, "{}.txt".format(date), backup_str)
    else:
        print(statement_fmt.format(message))

    print()

@client.command()
async def get_permissions(message):
    print(message.channel.permissions_for(message.author))

# -----------------------
# -    SHUTDOWN BOT     -
# -----------------------

@client.command(aliases = ['shutdown', 'turn_off'])
async def off(message):
    time = await getTimeStr()
    print("{} attempted shutdown at {}".format(message.author, time))

    if moderator_id in [role.id for role in message.author.roles]:
        print("Shutdown successful.")
        await message.channel.send("Shutting down.")
        await client.logout()
    else:
        print("Shutdown failed.")

# -----------------------
# -        TASKS        -
# -----------------------

status = ['Type "{}help" to learn more!'.format(client.command_prefix),
            "Eye'm the strongest!",
            "Beep boop, I'm a bot!"]
async def cycle_status():
    await client.wait_until_ready()
    msgs = cycle(status)

    while True:
        status_msg = next(msgs)
        await client.change_presence(activity = discord.Game(name = status_msg))
        await asyncio.sleep(15)

# -----------------------
# -       RUN BOT       -
# -----------------------

@client.event
async def on_ready():
    print(botname + " v" + bot_version + " ready!")
    print("discord.py API v" + discord.__version__)
    print("----------------------------")

    #TODO COMMENT OUT WHEN DONE WITH RUNTIME TESTING
    #exit()


client.loop.create_task(cycle_status())
client.run(TOKEN)
