import os
WATCHED_RESTAURANTS = {"KICKBACK JACK'S", "KICK BACK JACK'S"}
NOTIFICATION_CHANNEL_ID = 1524147758628475063


DISCORD_TOKEN = os.getenv("DISCOR_TOKEN")

COUNTIES = {
    "PITT": {
        "url": "https://public.cdpehs.com/NCENVPBL/ESTABLISHMENT/ShowESTABLISHMENTTablePage.aspx?ESTTST_CTY=74",
        "parser": "standard",
    },
    "WAKE": {
        "url": "https://public.cdpehs.com/NCENVPBL/ESTABLISHMENT/ShowESTABLISHMENTTablePage.aspx?ESTTST_CTY=92",
        "parser": "standard",
    },
    "DURHAM": {
        "url": "https://public.cdpehs.com/NCENVPBL/ESTABLISHMENT/ShowESTABLISHMENTTablePage.aspx?ESTTST_CTY=32",
        "parser": "standard",
    },
    "CUMBERLAND": {
        "url": "https://public.cdpehs.com/NCENVPBL/ESTABLISHMENT/ShowESTABLISHMENTTablePage.aspx?ESTTST_CTY=26",
        "parser": "standard",
    },
    "RANDOLPH": {
        "url": "https://public.cdpehs.com/NCENVPBL/ESTABLISHMENT/ShowESTABLISHMENTTablePage.aspx?ESTTST_CTY=76",
        "parser": "standard",
    },
    "GUILFORD": {
        "url": "https://public.cdpehs.com/NCENVPBL/ESTABLISHMENT/ShowESTABLISHMENTTablePage.aspx?ESTTST_CTY=41",
        "parser": "standard",
    },
    "CATAWBA": {
        "url": "https://public.cdpehs.com/NCENVPBL/ESTABLISHMENT/ShowESTABLISHMENTTablePage.aspx?ESTTST_CTY=18",
        "parser": "standard",
    },
    "IREDELL": {
        "url": "https://public.cdpehs.com/NCENVPBL/ESTABLISHMENT/ShowESTABLISHMENTTablePage.aspx?ESTTST_CTY=49",
        "parser": "standard",
    },
    "MOORE": {
        "url": "https://public.cdpehs.com/NCENVPBL/ESTABLISHMENT/ShowESTABLISHMENTTablePage.aspx?ESTTST_CTY=63",
        "parser": "standard",
    },
    "NEW HANOVER": {
        "url": "https://public.cdpehs.com/NCENVPBL/ESTABLISHMENT/ShowESTABLISHMENTTablePage.aspx?ESTTST_CTY=65",
        "parser": "standard",
    },
    "FORSYTH": {
        "url": "https://public.cdpehs.com/NCENVPBL/ESTABLISHMENT/ShowESTABLISHMENTTablePage.aspx?ESTTST_CTY=34",
        "parser": "standard",
    },
}


CATEGORY_IDS = {
    "PITT": 1523729817621495878,
    "WAKE": 1524026051305410641,
    "DURHAM": 1526953362342285332,
    "CUMBERLAND": 1526953424770306178,
    "RANDOLPH": 1528512085330231498,
    "GUILFORD": 1528512902573719723,
    "CATAWBA": 1528513458855739492,
    "IREDELL": 1528514028417187930,
    "MOORE": 1528514508732240004,
    "NEW HANOVER": 1528515057879879773,
    "FORSYTH": 1528515490111160471,
}


HITLIST_CHANNELS = {
    "PITT": 1524485988162867210,
    "WAKE": 1524485925327999186,
    "DURHAM": 1526955068656455802,
    "CUMBERLAND": 1526955094350889010,
    "RANDOLPH": 1528512144096624701,
    "GUILFORD": 1528512935394148404,
    "CATAWBA": 1528513536207360041,
    "IREDELL": 1528514085564579970,
    "MOORE": 1528514540420202618,
    "NEW HANOVER": 1528515101018165350,
    "FORSYTH": 1528515533454970963,
}
