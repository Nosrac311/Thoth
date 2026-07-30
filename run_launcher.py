from launcher.main import main
import sys
import signal
import multiprocessing

from launcher.manager import ServiceManager
from database import initialize_database


manager = ServiceManager()


def shutdown():

    print("Stopping all services...")

    manager.stop_all()

    print("Shutdown complete")

    sys.exit(0)


signal.signal(
    signal.SIGINT,
    lambda s, f: shutdown()
)


if __name__ == "__main__":

    multiprocessing.freeze_support()

    initialize_database()

    main()
