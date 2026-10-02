import asyncio
import traceback

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
    get_watchers,
)

from github_sync import sync_inspections_to_github


LOG_CHANNEL_ID = 1524018943197581352
WATCH_CHANNEL_ID = 1524147758628475063

POLL_INTERVAL = 300


# --------------- BACKGROUND LOOP ----------------


async def monitor(client):

    await client.wait_until_ready()

    print("Monitor started")

    try:

        async with aiohttp.ClientSession() as session:

            while not client.is_closed():

                try:

                    watch_channel = client.get_channel(
                        WATCH_CHANNEL_ID
                    )

                    # Keep track of every source that received
                    # at least one new inspection during this cycle.
                    new_sources = set()

                    # --------------------------------------------------
                    # Fetch all counties at once
                    # --------------------------------------------------

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

                    # --------------------------------------------------
                    # Process inspections
                    # --------------------------------------------------

                    for (source, _), inspections in zip(
                        COUNTIES.items(),
                        results,
                    ):

                        for data in reversed(inspections):

                            # --------------------------------------------------
                            # Already stored?
                            # --------------------------------------------------

                            if inspection_exists(
                                data["source"],
                                data["id"],
                                data["date"],
                            ):

                                continue


                            # --------------------------------------------------
                            # This is a NEW inspection
                            # --------------------------------------------------

                            new_sources.add(
                                data["source"]
                            )


                            # --------------------------------------------------
                            # Find/create inspector channel
                            # --------------------------------------------------

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


                            # --------------------------------------------------
                            # Create inspector channel if needed
                            # --------------------------------------------------

                            if channel is None:

                                if not client.guilds:

                                    print(
                                        "⚠️ No Discord guilds available "
                                        "to create inspector channel."
                                    )

                                    continue


                                guild = client.guilds[0]


                                category = guild.get_channel(
                                    CATEGORY_IDS[
                                        data["source"]
                                    ]
                                )


                                channel = await guild.create_text_channel(

                                    name=data["inspector_id"]
                                    .lower()
                                    .replace(" ", "-"),

                                    category=category,

                                )


                                save_inspector_channel(
                                    data["inspector_id"],
                                    channel.id,
                                )


                                # --------------------------------------------------
                                # Log new inspector channel
                                # --------------------------------------------------

                                log_channel = client.get_channel(
                                    LOG_CHANNEL_ID
                                )


                                if log_channel is None:

                                    try:

                                        log_channel = (
                                            await client.fetch_channel(
                                                LOG_CHANNEL_ID
                                            )
                                        )

                                    except discord.NotFound:

                                        log_channel = None


                                if log_channel:

                                    await log_channel.send(

                                        f"✅ Created channel "
                                        f"{channel.mention} "
                                        f"for inspector "
                                        f"**{data['inspector_id']}** "
                                        f"({data['source']})."

                                    )


                            # --------------------------------------------------
                            # Send inspection to inspector channel
                            # --------------------------------------------------

                            await channel.send(
                                embed=make_embed(data)
                            )


                            # --------------------------------------------------
                            # Save inspection to SQLite
                            # --------------------------------------------------

                            save_inspection(
                                data["source"],
                                data,
                            )


                            # --------------------------------------------------
                            # USER-SPECIFIC WATCHLIST
                            #
                            # Find all users whose watchlist contains
                            # this restaurant name.
                            #
                            # Example:
                            #
                            # User 1 -> ABC RESTAURANT
                            # User 2 -> MCDONALDS
                            #
                            # If this inspection is for ABC RESTAURANT,
                            # get_watchers() returns [1].
                            # --------------------------------------------------

                            watchers = get_watchers(
                                data["name"]
                            )


                            # --------------------------------------------------
                            # Watchlist alert
                            #
                            # For now this still posts to your existing
                            # Discord watch channel whenever at least one
                            # user is watching the restaurant.
                            #
                            # Later we can use the user IDs to send
                            # individual Discord DMs or push notifications.
                            # --------------------------------------------------

                            if watchers:

                                if watch_channel:

                                    await watch_channel.send(

                                        "🚨 **Watchlist Match!**",

                                        embed=make_embed(
                                            data
                                        ),

                                    )

                                    print(
                                        f"🚨 Watchlist match: "
                                        f"{data['name']} "
                                        f"| Users: {watchers}"
                                    )


                            # --------------------------------------------------
                            # Update restaurant statistics
                            # --------------------------------------------------

                            intervals = get_intervals(

                                get_restaurant_history(
                                    data["name"],
                                    data["source"],
                                )

                            )


                            if intervals:

                                update_stats(

                                    data["source"],

                                    data["name"],

                                    intervals[-1],

                                )


                    # --------------------------------------------------
                    # Update forecasts for every source with new data
                    # --------------------------------------------------

                    if new_sources:

                        forecast_cog = client.get_cog(
                            "Forecast"
                        )


                        if forecast_cog:

                            for source in sorted(
                                new_sources
                            ):

                                try:

                                    await forecast_cog.update_forecast(
                                        source
                                    )

                                except Exception:

                                    print(
                                        f"❌ Failed to update forecast "
                                        f"for {source}"
                                    )

                                    traceback.print_exc()


                    # --------------------------------------------------
                    # Sync new inspection data to GitHub
                    #
                    # This happens AFTER all counties have been processed,
                    # so there is only ONE GitHub commit for the entire
                    # polling cycle.
                    # --------------------------------------------------

                    if new_sources:

                        try:

                            await asyncio.to_thread(
                                sync_inspections_to_github
                            )

                        except Exception:

                            print(
                                "❌ GitHub inspection sync failed. "
                                "The Discord monitor will continue."
                            )

                            traceback.print_exc()


                # --------------------------------------------------
                # Cancellation
                # --------------------------------------------------

                except asyncio.CancelledError:

                    print(
                        "Monitor cancellation requested"
                    )

                    raise


                # --------------------------------------------------
                # Prevent one failure from killing monitor
                # --------------------------------------------------

                except Exception:

                    traceback.print_exc()


                # --------------------------------------------------
                # Wait until next polling cycle
                # --------------------------------------------------

                await asyncio.sleep(
                    POLL_INTERVAL
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
