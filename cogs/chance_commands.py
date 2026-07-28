from discord.ext import commands
from discord import app_commands
import discord

from database import (
    get_connection,
    get_restaurant_history,
    get_distribution_params,
)

from prediction import (  # type: ignore
    get_intervals,
    parse_date,
    inspector_pressure,
    grade_risk,
    build_bayesian_model,
    probability_distribution,
    get_prediction_window
)


def query_one(sql, params=()):

    db = get_connection()
    cursor = db.cursor()

    cursor.execute(
        sql,
        params
    )

    row = cursor.fetchone()

    db.close()

    return row


def execute(sql, params=()):

    db = get_connection()

    db.execute(
        sql,
        params
    )

    db.commit()

    db.close()


class UtilityCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="chance",
        description="Estimate inspection likelihood."
    )
    @app_commands.describe(
        name="Restaurant name",
        source="County source (PITT or WAKE)"
    )
    async def chance(
        self,
        interaction: discord.Interaction,
        name: str,
        source: str
    ):

        row = query_one(
            """
            SELECT restaurant, inspector_id, grade, inspection_date
            FROM inspections
            WHERE restaurant LIKE ?
            AND source = ?
            ORDER BY inspection_date DESC
            LIMIT 1
            """,
            (
                f"%{name}%",
                source.upper()
            )
        )

        if not row:
            await interaction.response.send_message(
                "No restaurant found.",
                ephemeral=True
            )
            return

        restaurant, inspector_id, grade, last_date = row

        dates = get_restaurant_history(
            restaurant,
            source.upper()
        )

        if len(dates) < 2:
            avg_interval = 120
        else:
            intervals = get_intervals(dates)
            avg_interval = sum(intervals) / len(intervals)

        mu, var = get_distribution_params(
            restaurant,
            source.upper()
        )

        inspector_p = inspector_pressure(inspector_id)
        grade_p = grade_risk(grade)

        mu, sigma = build_bayesian_model(
            mu,
            var,
            inspector_p,
            grade_p
        )

        dist = probability_distribution(
            mu,
            sigma,
            days=30
        )

        start, end = get_prediction_window(dist)

        peak_day = max(
            dist,
            key=lambda x: x[1]
        )[0]

        embed = discord.Embed(
            title=f"Inspection Prediction: {restaurant}"
        )

        embed.add_field(
            name="Most Likely Window",
            value=f"{start} – {end} days from now",
            inline=False
        )

        embed.add_field(
            name="Peak Likelihood",
            value=f"~{peak_day} days from now",
            inline=False
        )

        embed.add_field(
            name="Model Inputs",
            value=(
                f"Inspector load: {round(inspector_p * 100, 1)}%\n"
                f"Grade risk: {round(grade_p * 100, 1)}%\n"
                f"Avg interval: {round(avg_interval, 1)} days"
            ),
            inline=False
        )

        await interaction.response.send_message(
            embed=embed
        )

    @app_commands.command(
        name="watchadd",
        description="Add a restaurant to the watchlist."
    )
    async def watchadd(
        self,
        interaction: discord.Interaction,
        restaurant: str
    ):

        execute(
            """
            INSERT OR IGNORE INTO watchlist
            VALUES (?)
            """,
            (
                restaurant.upper(),
            )
        )

        await interaction.response.send_message(
            f"✅ **{restaurant}** added to watchlist.",
            ephemeral=True
        )

    @app_commands.command(
        name="watchremove",
        description="Remove a restaurant from the watchlist."
    )
    async def watchremove(
        self,
        interaction: discord.Interaction,
        restaurant: str
    ):

        execute(
            """
            DELETE FROM watchlist
            WHERE restaurant = ?
            """,
            (
                restaurant.upper(),
            )
        )

        await interaction.response.send_message(
            f"🗑️ Removed **{restaurant}**.",
            ephemeral=True
        )

    @app_commands.command(
        name="watchlist",
        description="Show all watched restaurants."
    )
    async def watchlist(
        self,
        interaction: discord.Interaction
    ):

        db = get_connection()
        cursor = db.cursor()

        cursor.execute(
            """
            SELECT restaurant
            FROM watchlist
            ORDER BY restaurant
            """
        )

        rows = cursor.fetchall()

        db.close()

        if not rows:
            await interaction.response.send_message(
                "The watchlist is empty.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="👀 Restaurant Watchlist",
            color=discord.Color.green()
        )

        embed.description = "\n".join(
            f"• {r[0]}"
            for r in rows
        )

        await interaction.response.send_message(
            embed=embed
        )


async def setup(bot):
    await bot.add_cog(UtilityCommands(bot))
