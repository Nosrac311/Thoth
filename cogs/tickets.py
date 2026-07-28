from discord.ext import commands
from discord import app_commands
from views.ticket_view import TicketView


class Tickets(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="ticketpanel",
        description="Post the ticket panel"
    )
    async def ticketpanel(
        self,
        interaction
    ):

        await interaction.response.send_message(
            "Command Zone",
            view=TicketView()
        )


async def setup(bot):
    await bot.add_cog(Tickets(bot))
