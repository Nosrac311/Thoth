import discord
from datetime import datetime
from zoneinfo import ZoneInfo
import asyncio


TICKET_CATEGORY_ID = 1524017658188660807
SUPPORT_ROLE_ID = 1524017896043577487
AUTO_CLOSE_TIME = 3600


class TicketView(discord.ui.View):

    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    async def auto_close_ticket(self, channel: discord.TextChannel):
        await asyncio.sleep(AUTO_CLOSE_TIME)

        try:
            await channel.send(
                "⏰ This ticket has been automatically closed because it reached the time limit."
            )

            await channel.delete(
                reason="Ticket auto-closed after timeout."
            )

        except discord.NotFound:
            pass

        except discord.Forbidden:
            print(f"Missing permissions to delete {channel.name}")

    @discord.ui.button(
        label="Command Zone",
        emoji="🎫",
        style=discord.ButtonStyle.green,
        custom_id="create_ticket"
    )
    async def create_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        now = datetime.now(
            ZoneInfo("America/New_York")
        )

        if now.weekday() >= 5 or not (9 <= now.hour < 17):
            await interaction.response.send_message(
                "🚫 Command Zone is currently closed.\n"
                "**Hours:** Monday–Friday, 9:00 AM – 5:00 PM (ET).",
                ephemeral=True
            )
            return

        guild = interaction.guild
        user = interaction.user

        existing = discord.utils.get(
            guild.text_channels,
            name=f"ticket-{user.id}"
        )

        if existing:
            await interaction.response.send_message(
                "You already have an open ticket.",
                ephemeral=True
            )
            return

        category = guild.get_channel(
            TICKET_CATEGORY_ID
        )

        support = guild.get_role(
            SUPPORT_ROLE_ID
        )

        overwrites = {
            guild.default_role:
                discord.PermissionOverwrite(
                    view_channel=False
                ),

            user:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                ),

            support:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                ),

            guild.me:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    manage_channels=True,
                    manage_messages=True
                )
        }

        channel = await guild.create_text_channel(
            name=f"ticket-{user.id}",
            category=category,
            overwrites=overwrites
        )

        await channel.send(
            f"{user.mention} Welcome! A member of {support.mention} "
            "will be with you shortly.\n\n"
            f"⏳ **This ticket will automatically close in "
            f"{AUTO_CLOSE_TIME // 60} minutes.**"
        )

        asyncio.create_task(
            self.auto_close_ticket(channel)
        )

        await interaction.response.send_message(
            f"✅ Your ticket has been created: {channel.mention}",
            ephemeral=True
        )
