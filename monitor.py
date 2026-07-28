import asyncio

import aiohttp
import discord

from config import COUNTIES, CATEGORY_IDS
from embed import make_embed
from prediction import get_intervals
from scraper import get_inspections

from database import (
    inspection_exists,
    save_inspection,
    get_restaurant_history,
    update_stats,
    get_inspector_channel,
    save_inspector_channel,
    get_watchlist,
)


LOG_CHANNEL_ID = 1524018943197581352
# --------------- BACKGROUND LOOP ----------------


async def monitor(client):

    await client.wait_until_ready()

    print("Monitor started")

    try:

        async with aiohttp.ClientSession() as session:

            while not client.is_closed():

                try:

                    watched = get_watchlist()

                    watch_channel = client.get_channel(
                        1524147758628475063
                    )

                    # Fetch all counties at once
                    tasks = [
                        get_inspections(
                            session,
                            county["url"],
                            source,
                            county["parser"],
                        )

                        for source, county in COUNTIES.items()
                    ]

                    results = await asyncio.gather(
                        *tasks
                    )

                    for (source, _), inspections in zip(
                        COUNTIES.items(),
                        results
                    ):

                        new_inspections = False

                        for data in reversed(inspections):

                            if inspection_exists(
                                data["source"],
                                data["id"],
                                data["date"]
                            ):
                                continue

                            new_inspections = True

                            channel_id = get_inspector_channel(
                                data["inspector_id"]
                            )

                            channel = None

                            if channel_id:

                                channel = client.get_channel(
                                    channel_id
                                )

                                if channel is None:

                                    try:

                                        channel = await client.fetch_channel(
                                            channel_id
                                        )

                                    except discord.NotFound:

                                        channel = None

                            if channel is None:

                                guild = client.guilds[0]

                                category = guild.get_channel(
                                    CATEGORY_IDS[data["source"]]
                                )

                                channel = await guild.create_text_channel(
                                    name=data["inspector_id"]
                                    .lower()
                                    .replace(" ", "-"),

                                    category=category
                                )

                                save_inspector_channel(
                                    data["inspector_id"],
                                    channel.id
                                )

                                log_channel = client.get_channel(
                                    LOG_CHANNEL_ID
                                )

                                if log_channel is None:

                                    log_channel = await client.fetch_channel(
                                        LOG_CHANNEL_ID
                                    )

                                await log_channel.send(
                                    f"✅ Created channel {channel.mention} "
                                    f"for inspector **{data['inspector_id']}** "
                                    f"({data['source']})."
                                )

                            await channel.send(
                                embed=make_embed(data)
                            )

                            save_inspection(
                                data["source"],
                                data
                            )

                            restaurant_name = data["name"].upper()

                            for watched_name in watched:

                                if watched_name.upper() in restaurant_name:

                                    if watch_channel:

                                        await watch_channel.send(
                                            "🚨 **Watchlist Match!**",
                                            embed=make_embed(data)
                                        )

                                    break

                            intervals = get_intervals(
                                get_restaurant_history(
                                    data["name"],
                                    data["source"]
                                )
                            )

                            if intervals:

                                update_stats(
                                    data["source"],
                                    data["name"],
                                    intervals[-1]
                                )

                        if new_inspections:

                            forecast_cog = client.get_cog(
                                "Forecast"
                            )

                            if forecast_cog:

                                await forecast_cog.update_forecast(
                                    source
                                )

                except asyncio.CancelledError:

                    print(
                        "Monitor cancellation requested"
                    )

                    raise

                except Exception:

                    import traceback
                    traceback.print_exc()

                # Wait 5 minutes, but allow cancellation
                await asyncio.sleep(
                    300
                )

    except asyncio.CancelledError:

        print(
            "Monitor shutting down"
        )

        raise

    finally:

        print(
            "Monitor stopped"
        )
