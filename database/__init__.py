from database.connection import (
    get_connection,
    database_path,
)

from database.inspections import *
from database.channels import *
from database.forecast import *
from database.stats import *
from database.watchlist import *
from database.user import *


from database.inspections import (
    init as init_inspections
)

from database.channels import (
    init as init_channels
)

from database.forecast import (
    init as init_forecasts
)

from database.stats import (
    init as init_stats
)

from database.user import (
    init as init_users
)

from database.watchlist import (
    init as init_watchlist
)


def initialize_database():

    init_inspections()

    init_channels()

    init_forecasts()

    init_stats()

    # Users MUST exist before
    # watchlist's foreign key references them.

    init_users()

    init_watchlist()


initialize_database()
