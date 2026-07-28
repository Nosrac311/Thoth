from bs4 import BeautifulSoup
from datetime import datetime


async def fetch_html(session, url, source):
    try:
        async with session.get(url, timeout=30) as res:
            res.raise_for_status()
            return await res.text()
    except Exception as e:
        print(f"{source}: {e}")
        return None


def parse_standard_site(html, source):
    soup = BeautifulSoup(html, "html.parser")

    table = soup.select_one("#VW_PUBLIC_ESTINSPTableControlGrid")

    if table is None:
        print(f"Could not find inspection table for {source}")
        return []

    inspections = []

    for row in table.find_all("tr")[1:]:
        values = [td.get_text(strip=True) for td in row.find_all("td")]

        if len(values) < 9:
            continue

        inspections.append({
            "source": source,
            "id": values[4],
            "date": datetime.strptime(
                values[1],
                "%m/%d/%Y"
            ).date().isoformat(),
            "name": values[2],
            "score": values[6],
            "grade": values[7],
            "inspector_id": values[8],
            "estab_type": values[5],
        })

    return inspections


# def parse_new_site(html, source):
    """
    Parser for your second website.
    Replace this with the new site's HTML parsing.
    """
    return []


async def get_inspections(session, url, source, parser="standard"):
    html = await fetch_html(session, url, source)

    if html is None:
        return []

    if parser == "standard":
        return parse_standard_site(html, source)

   # if parser == "new":
        return parse_new_site(html, source)

    raise ValueError(f"Unknown parser: {parser}")
