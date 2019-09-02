# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module which contains afk-related commands """

import time

from telethon.events import StopPropagation

from userbot import (BOTLOG, BOTLOG_CHATID, CMD_HELP, COUNT_MSG, USERS,
                     is_redis_alive)
from userbot.events import register, errors_handler
from userbot.modules.dbhelper import is_afk, afk, afk_reason, no_afk


@register(incoming=True, disable_edited=True)
@errors_handler
async def mention_afk(mention):
    """ This function takes care of notifying the
     people who mention you that you are AFK."""

    global COUNT_MSG
    global USERS
    if not is_redis_alive():
        return
    AFK = await is_afk()
    if mention.message.mentioned and not (await mention.get_sender()).bot:
        if AFK is True:
            if mention.sender_id not in USERS:
                await mention.reply(
                    "Scusa! Shadow è AFK per: " + await afk_reason() +
                    ". Gli manderò una notifica per guardare il messaggio😉.")
                USERS.update({mention.sender_id: 1})
                COUNT_MSG = COUNT_MSG + 1
            elif mention.sender_id in USERS:
                if USERS[mention.sender_id] % 5 == 0:
                    await mention.reply(
                        "Scusa! Ma shadow non è ancora tornato. "
                        "Prova a inviargli un messaggio tra un po'. Mi dispiace😖."
                        "Mi ha detto che era impegnato per ```" +
                        await afk_reason() + "```")
                    USERS[mention.sender_id] = USERS[mention.sender_id] + 1
                    COUNT_MSG = COUNT_MSG + 1
                else:
                    USERS[mention.sender_id] = USERS[mention.sender_id] + 1
                    COUNT_MSG = COUNT_MSG + 1


@register(incoming=True)
@errors_handler
async def afk_on_pm(e):
    global USERS
    global COUNT_MSG
    if not is_redis_alive():
        return
    AFK = await is_afk()
    if e.is_private and not (await e.get_sender()).bot:
        if AFK is True:
            if e.sender_id not in USERS:
                await e.reply(
                    "Scusa! Ma shadow è AFK per: ```" + await afk_reason() +
                    "```. Gli manderò una notifica per far vedere il tuo messaggio😉")
                USERS.update({e.sender_id: 1})
                COUNT_MSG = COUNT_MSG + 1
            elif e.sender_id in USERS:
                if USERS[e.sender_id] % 5 == 0:
                    await e.reply(
                        "Scusa! Ma shadow non è ancora tornato. "
                        "Prova a inviargli un messaggio tra un po'. Mi dispiace😖."
                        "Mi ha detto che era impegnato per ```" +
                        await afk_reason() + "```")
                    USERS[e.sender_id] = USERS[e.sender_id] + 1
                    COUNT_MSG = COUNT_MSG + 1
                else:
                    USERS[e.sender_id] = USERS[e.sender_id] + 1
                    COUNT_MSG = COUNT_MSG + 1


@register(outgoing=True, pattern="^.afk")
async def set_afk(e):
    if not e.text[0].isalpha() and e.text[0] not in ("/", "#", "@", "!"):
        if not is_redis_alive():
            await e.edit("`Database connections failing!`")
            return
        message = e.text
        try:
            AFKREASON = str(message[5:])
        except BaseException:
            AFKREASON = ''
        if not AFKREASON:
            AFKREASON = 'No reason'
        await e.edit("AFK Attivato!")
        if BOTLOG:
            await e.client.send_message(BOTLOG_CHATID, "You went AFK!")
        await afk(AFKREASON)
        raise StopPropagation


@register(outgoing=True)
@errors_handler
async def type_afk_is_not_true(e):
    global COUNT_MSG
    global USERS
    global AFKREASON
    if not is_redis_alive():
        return
    ISAFK = await is_afk()
    if ISAFK is True:
        await no_afk()
        x = await e.respond("Non sono più AFK.")
        y = await e.respond(
            "`Hai ricevuto " + str(COUNT_MSG) +
            " messaggi mentre eri fuori. Controlla i log per i dettagli.`" +
            " `Questo messaggio auto-generato " +
            "si distruggerà tra 2 secondi.`")
        time.sleep(2)
        await x.delete()
        await y.delete()
        if BOTLOG:
            await e.client.send_message(
                BOTLOG_CHATID,
                "Hai ricevuto " + str(COUNT_MSG) + " messaggi da " +
                str(len(USERS)) + " chat mentre eri impegnato",
            )
            for i in USERS:
                name = await e.client.get_entity(i)
                name0 = str(name.first_name)
                await e.client.send_message(
                    BOTLOG_CHATID,
                    "[" + name0 + "](tg://user?id=" + str(i) + ")" +
                    " ti ha mandato " + "`" + str(USERS[i]) + " messaggi`",
                )
        COUNT_MSG = 0
        USERS = {}
        AFKREASON = "Nessun motivo."


CMD_HELP.update({
    "afk":
    ".afk <reason>(optional)\
\nUsage: Sets your status as AFK. Responds to anyone who tags/PM's \
you telling you are AFK. Switches off AFK when you type back anything.\
"
})
