import requests
import time
import discord
from bs4 import BeautifulSoup
from discord import app_commands
from discord.ext import commands
from datetime import timedelta
from datetime import datetime
import sqlite3
import os
import math
import numpy as np


# ---------------- EMBED ----------------
def make_embed(data):
    embed = discord.Embed(
        title="🚨 New Health Inspection Alert",
        color=0xff4444
    )
    pretty_date = datetime.strptime(
        data["date"],
        "%Y-%m-%d"
    ).strftime("%m/%d/%Y")

    embed.add_field(name="Name", value=data["name"], inline=False)
    embed.add_field(name="Score", value=data["score"], inline=True)
    embed.add_field(name="Grade", value=data["grade"], inline=True)
    embed.add_field(name="Date", value=pretty_date, inline=False)
    embed.add_field(name="State ID", value=data["id"], inline=False)
    embed.add_field(name="Inspector ID",
                    value=data["inspector_id"], inline=False)
    embed.add_field(name="Establishment Type",
                    value=data["estab_type"], inline=False)

    return embed
