from discord.ext import commands
from discord import app_commands
import discord
from typing import Literal

from config import COUNTIES  # type: ignore
from scraper import get_inspections  # type: ignore
from embed import make_embed  # type: ignore
from database import get_connection  # type: ignore


INSPECTOR_COUNT_CHANNEL_ID = 1526957389016727594


class InspectionCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="latest",
        description="Show the latest inspection."
    )
    async def latest(
        self,
        interaction: discord.Interaction,
        county: Literal["PITT", "WAKE"]
    ):
        await interaction.response.defer()

        url = COUNTIES[county]

        inspections = await get_inspections(
            url,
            county
        )

        if not inspections:
            await interaction.followup.send(
                "No inspections found.",
                ephemeral=True
            )
            return

        await interaction.followup.send(
            embed=make_embed(inspections[0])
        )

    @app_commands.command(
        name="count",
        description="Show how many inspections are stored."
    )
    async def count(
        self,
        interaction: discord.Interaction
    ):

        db = get_connection()
        cursor = db.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM inspections"
        )

        total = cursor.fetchone()[0]

        db.close()

        await interaction.response.send_message(
            f"I currently have **{total}** inspections stored."
        )

    @app_commands.command(
        name="inspector",
        description="Show inspections for an inspector."
    )
    async def inspector(
        self,
        interaction: discord.Interaction,
        inspector_id: str
    ):

        db = get_connection()
        cursor = db.cursor()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM inspections
            WHERE inspector_id = ?
            """,
            (
                inspector_id,
            )
        )

        total = cursor.fetchone()[0]

        db.close()

        await interaction.response.send_message(
            f"Inspector **{inspector_id}** has **{total}** inspections in the database."
        )

    @app_commands.command(
        name="restaurant",
        description="Search restaurant inspections."
    )
    @app_commands.describe(
        name="Restaurant name"
    )
    async def restaurant(
        self,
        interaction: discord.Interaction,
        name: str
    ):

        db = get_connection()
        cursor = db.cursor()

        cursor.execute(
            """
            SELECT
                restaurant,
                inspection_date,
                score,
                grade
            FROM inspections
            WHERE restaurant LIKE ?
            ORDER BY inspection_date DESC
            LIMIT 10
            """,
            (
                f"%{name}%",
            )
        )

        rows = cursor.fetchall()

        db.close()

        if not rows:
            await interaction.response.send_message(
                "No matching restaurants found.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"Results for '{name}'"
        )

        for restaurant, date, score, grade in rows:

            embed.add_field(
                name=restaurant,
                value=(
                    f"{date}\n"
                    f"Score: {score}\n"
                    f"Grade: {grade}"
                ),
                inline=False
            )

        await interaction.response.send_message(
            embed=embed
        )

    @app_commands.command(
        name="update_inspector_count",
        description="Update the inspector channel count."
    )
    async def update_inspector_count(
        self,
        interaction: discord.Interaction
    ):

        await interaction.response.defer(
            ephemeral=True
        )

        db = get_connection()
        cursor = db.cursor()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM inspector_channels
            """
        )

        total = cursor.fetchone()[0]

        db.close()

        channel = self.bot.get_channel(
            INSPECTOR_COUNT_CHANNEL_ID
        )

        if channel is None:

            channel = await self.bot.fetch_channel(
                INSPECTOR_COUNT_CHANNEL_ID
            )

        await channel.edit(
            name=f"👤 Inspectors: {total}"
        )

        await interaction.followup.send(
            f"Updated inspector count to {total}.",
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(
        InspectionCommands(bot)
    )
