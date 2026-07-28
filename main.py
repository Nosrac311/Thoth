import discord
from discord.ext import commands

from config import TOKEN
from views.ticket_view import TicketView
from monitor import monitor

import asyncio
import os
import signal


intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

shutdown_event = asyncio.Event()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


async def setup_hook():

    await bot.load_extension("cogs.chance_commands")
    await bot.load_extension("cogs.forecast")
    await bot.load_extension("cogs.inspections_commands")
    await bot.load_extension("cogs.reaction_roles")
    await bot.load_extension("cogs.tickets")

    bot.add_view(
        TicketView(bot)
    )

    bot.monitor_task = asyncio.create_task(
        monitor(bot)
    )

    await bot.tree.sync()


bot.setup_hook = setup_hook


def handle_shutdown():

    print("Shutdown signal received")

    asyncio.create_task(
        shutdown()
    )


@bot.event
async def on_ready():

    print(
        f"Logged in as {bot.user}"
    )


@bot.event
async def on_disconnect():

    print(
        "Bot disconnected from Discord"
    )


async def shutdown():

    print("Shutting down bot...")

    if hasattr(bot, "monitor_task"):

        print("Stopping monitor")

        bot.monitor_task.cancel()

        try:
            await bot.monitor_task

        except asyncio.CancelledError:
            pass

    await bot.close()

    shutdown_event.set()


def console_handler(sig, frame):

    print("Console shutdown detected")

    asyncio.create_task(
        shutdown()
    )


async def main():

    print("Starting bot...")

    signal.signal(
        signal.SIGINT,
        console_handler
    )

    signal.signal(
        signal.SIGTERM,
        console_handler
    )

    print("Launching Discord connection")

    bot_task = asyncio.create_task(
        bot.start(TOKEN)
    )

    await shutdown_event.wait()

    print("Shutdown event triggered")

    if not bot.is_closed():
        await shutdown()

    await bot_task


def run_bot():
    asyncio.run(main())


if __name__ == "__main__":
    run_bot()
