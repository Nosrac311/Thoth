from multiprocessing import Process


def run_bot_process():

    from main import run_bot

    run_bot()


def run_dashboard_process():

    from app.api import run_dashboard

    run_dashboard()


class ServiceManager:

    def __init__(self):

        self.bot = None
        self.dashboard = None

    def start_services(self):

        if self.bot is None or not self.bot.is_alive():

            self.bot = Process(
                target=run_bot_process,
                name="Discord Bot",
                daemon=True
            )

            self.bot.start()

        if self.dashboard is None or not self.dashboard.is_alive():

            self.dashboard = Process(
                target=run_dashboard_process,
                name="FastAPI Dashboard",
                daemon=True
            )

            self.dashboard.start()

    def stop_bot(self):

        if self.bot and self.bot.is_alive():

            print("Stopping Discord Bot")

            self.bot.terminate()
            self.bot.join(timeout=10)

    def stop_dashboard(self):

        if self.dashboard and self.dashboard.is_alive():

            print("Stopping Dashboard")

            self.dashboard.terminate()
            self.dashboard.join(timeout=10)

    def stop_all(self):

        print("Stopping all services...")

        self.stop_bot()
        self.stop_dashboard()

        print("All services stopped")

    def restart_bot(self):

        self.stop_bot()

        self.bot = Process(
            target=run_bot_process,
            name="Discord Bot",
            daemon=True
        )

        self.bot.start()

    def restart_dashboard(self):

        self.stop_dashboard()

        self.dashboard = Process(
            target=run_dashboard_process,
            name="FastAPI Dashboard",
            daemon=True
        )

        self.dashboard.start()

    def status(self):

        return {

            "Discord Bot":
                "ONLINE"
                if self.bot and self.bot.is_alive()
                else "STOPPED",


            "FastAPI Dashboard":
                "ONLINE"
                if self.dashboard and self.dashboard.is_alive()
                else "STOPPED"

        }
