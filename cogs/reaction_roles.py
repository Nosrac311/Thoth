import discord
from discord.ext import commands
from discord import app_commands
import json
import os


REACTION_FILE = "reaction_roles.json"


class ReactionRoles(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="reactionrole",
        description="Create a reaction role message"
    )
    @app_commands.default_permissions(manage_roles=True)
    async def reactionrole(
        self,
        interaction: discord.Interaction,
        title: str,
        description: str,
        emoji1: str,
        role1: discord.Role,
        emoji2: str,
        role2: discord.Role
    ):

        embed = discord.Embed(
            title=title,
            description=(
                f"{description}\n\n"
                f"{emoji1} {role1.mention}\n"
                f"{emoji2} {role2.mention}"
            ),
            color=discord.Color.blurple()
        )

        message = await interaction.channel.send(
            embed=embed
        )

        await message.add_reaction(emoji1)
        await message.add_reaction(emoji2)

        data = {}

        if os.path.exists(REACTION_FILE):
            with open(REACTION_FILE, "r") as f:
                data = json.load(f)

        data[str(message.id)] = {
            emoji1: role1.id,
            emoji2: role2.id
        }

        with open(REACTION_FILE, "w") as f:
            json.dump(
                data,
                f,
                indent=4
            )

        await interaction.response.send_message(
            "Reaction role message created!",
            ephemeral=True
        )

    @commands.Cog.listener()
    async def on_raw_reaction_add(
        self,
        payload: discord.RawReactionActionEvent
    ):

        if payload.user_id == self.bot.user.id:
            return

        data = self.load_roles()

        message_id = str(payload.message_id)

        if message_id not in data:
            return

        emoji = str(payload.emoji)

        if emoji not in data[message_id]:
            return

        guild = self.bot.get_guild(
            payload.guild_id
        )

        if guild is None:
            return

        member = guild.get_member(
            payload.user_id
        )

        if member is None:
            return

        role = guild.get_role(
            data[message_id][emoji]
        )

        if role:
            await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(
        self,
        payload: discord.RawReactionActionEvent
    ):

        data = self.load_roles()

        message_id = str(payload.message_id)

        if message_id not in data:
            return

        emoji = str(payload.emoji)

        if emoji not in data[message_id]:
            return

        guild = self.bot.get_guild(
            payload.guild_id
        )

        if guild is None:
            return

        member = guild.get_member(
            payload.user_id
        )

        if member is None:
            return

        role = guild.get_role(
            data[message_id][emoji]
        )

        if role:
            await member.remove_roles(role)

    def load_roles(self):

        if not os.path.exists(REACTION_FILE):
            return {}

        with open(REACTION_FILE, "r") as f:
            return json.load(f)


async def setup(bot):
    await bot.add_cog(
        ReactionRoles(bot)
    )
