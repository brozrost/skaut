# scraper.py
#
# Scrapes Bazoš search-result pages.
#
# The HTML structure this scraper expects is:
#
# <div class="inzeraty inzeratyflex">
#     <h2 class="nadpis">
#         <a href="/inzerat/221817487/example.php">Title</a>
#     </h2>
#
#     <div class="popis">Description...</div>
#     <div class="inzeratycena">149 800 Kč</div>
#     <div class="inzeratylok">Bruntál<br>792 01</div>
#     <div class="inzeratyview">140 x</div>
# </div>
#
# This matches the source you supplied. :contentReference[oaicite:0]{index=0}

import re
import time
from dataclasses import dataclass
from urllib.parse import urljoin
from urllib.parse import urlparse, urlunparse

import requests
from bs4 import BeautifulSoup, Tag


# Used to convert relative links such as:
# /inzerat/221817487/example.php
#
# into:
# https://auto.bazos.cz/inzerat/221817487/example.php
BASE_URL = "https://www.bazos.cz"


# Identify the client making the request.
HEADERS = {
    "User-Agent": "ListScout/0.1"
}


@dataclass
class Listing:
    """
    Represents one advertisement extracted from a Bazoš result page.
    """

    id: str
    title: str
    url: str
    description: str | None
    price: str | None
    location: str | None
    views: str | None


def get_text(element: Tag | None) -> str | None:
    """
    Return cleaned text from an HTML element.

    Example HTML:

        <div class="inzeratylok">
            Bruntál<br>
            792 01
        </div>

    Result:

        "Bruntál 792 01"

    If the element does not exist, return None.
    """

    if element is None:
        return None

    text = element.get_text(" ", strip=True)

    return text or None


def extract_listing_id(url: str) -> str:
    """
    Extract the numeric advertisement ID from its URL.

    Example:

        /inzerat/221817487/example.php

    Result:

        221817487
    """

    match = re.search(r"/inzerat/(\d+)/", url)

    if match is None:
        raise ValueError(f"Invalid Bazoš listing URL: {url}")

    return match.group(1)


def parse_listing(element: Tag, page_url: str) -> Listing | None:
    """
    Parse one <div class="inzeraty"> result container.

    The method searches only inside the supplied container, so the price,
    location and description belong to the same advertisement.
    """

    # The title is inside:
    #
    # <h2 class="nadpis">
    #     <a href="/inzerat/...">Title</a>
    # </h2>
    title_link = element.select_one(
        'h2.nadpis > a[href*="/inzerat/"]'
    )

    if title_link is None:
        return None

    href = title_link.get("href")

    if not isinstance(href, str):
        return None

    # urljoin uses the current subdomain.
    #
    # For example, when page_url is:
    # https://auto.bazos.cz/
    #
    # the resulting listing URL remains on auto.bazos.cz.
    listing_url = urljoin(page_url, href)

    return Listing(
        id=extract_listing_id(listing_url),
        title=title_link.get_text(" ", strip=True),
        url=listing_url,

        # In your source the description uses:
        # <div class=popis>...</div>
        description=get_text(
            element.select_one(".popis")
        ),

        # Price uses:
        # <div class="inzeratycena">...</div>
        price=get_text(
            element.select_one(".inzeratycena")
        ),

        # Location uses:
        # <div class="inzeratylok">...</div>
        location=get_text(
            element.select_one(".inzeratylok")
        ),

        # View count uses:
        # <div class="inzeratyview">140 x</div>
        views=get_text(
            element.select_one(".inzeratyview")
        ),
    )


def find_next_page(
    soup: BeautifulSoup,
    current_url: str,
) -> str | None:
    """
    Find the link whose visible text is 'Další'.

    This checks get_text() rather than BeautifulSoup's string= argument.
    That matters because Bazoš may wrap the word inside another tag:

        <a href="/20/">
            <b>Další</b>
        </a>

    In that case the anchor does not contain a direct text node, but
    link.get_text(strip=True) still correctly returns 'Další'.
    """

    for link in soup.find_all("a", href=True):
        if link.get_text(" ", strip=True).casefold() == "další":
            href = link.get("href")

            if isinstance(href, str):
                return urljoin(current_url, href)

    return None


def scrape_page(
    url: str,
    session: requests.Session | None = None,
) -> tuple[list[Listing], str | None]:
    """
    Download and parse one result page.

    Returns:

        (
            list of listings,
            next page URL or None
        )
    """

    # Reusing a Session is more efficient when scraping multiple pages,
    # because HTTP connections can be reused.
    client = session or requests.Session()

    response = client.get(
        url,
        headers=HEADERS,
        timeout=15,
    )

    # Raise an exception for 4xx and 5xx responses.
    response.raise_for_status()

    # Bazoš declares UTF-8 in the HTML source, so requests should normally
    # detect it correctly. This assignment makes the choice explicit.
    response.encoding = "utf-8"

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    listings: list[Listing] = []

    # Only actual advertisements use both classes:
    #
    # <div class="inzeraty inzeratyflex">
    #
    # The table header instead uses:
    #
    # <div class="listainzerat inzeratyflex">
    #
    # so this selector does not accidentally parse the header.
    listing_elements = soup.select(
        "div.inzeraty.inzeratyflex"
    )

    for element in listing_elements:
        listing = parse_listing(
            element,
            response.url,
        )

        if listing is not None:
            listings.append(listing)

    next_page = find_next_page(
        soup,
        response.url,
    )

    return listings, next_page

def scrape_all_pages(
    start_url: str,
    delay: float = 1.0,
    max_pages: int = 5,
) -> list[Listing]:
    """
    Scrape every available result page.

    Parameters:

        start_url:
            First search-result URL.

        delay:
            Number of seconds to wait between page requests.

        max_pages:
            Optional development limit.

            For example, max_pages=3 scrapes at most three pages.
            None means no artificial limit.

    Results are deduplicated using the numeric listing ID.
    """

    listings_by_id: dict[str, Listing] = {}

    with requests.Session() as session:

        for page in range(max_pages):

            if page == 0:
                url = start_url
            else:
                offset = page * 20

                parsed = urlparse(start_url)

                # insert "/20/", "/40/", ... before the query string
                path = f"/{offset}/"

                url = urlunparse((
                    parsed.scheme,
                    parsed.netloc,
                    path,
                    "",
                    parsed.query,
                    "",
                ))

            print(f"Scraping {url}")

            page_listings, _ = scrape_page(url, session)

            if not page_listings:
                print("No listings found, stopping.")
                break

            for listing in page_listings:
                listings_by_id[listing.id] = listing

            print(f"Found {len(page_listings)} listings")

            time.sleep(delay)

    return list(listings_by_id.values())


def print_listing(listing: Listing) -> None:
    """
    Print one listing in a readable terminal format.
    """

    print(f"ID:          {listing.id}")
    print(f"Title:       {listing.title}")
    print(f"Price:       {listing.price}")
    print(f"Location:    {listing.location}")
    print(f"Views:       {listing.views}")
    print(f"Description: {listing.description}")
    print(f"URL:         {listing.url}")
    print("-" * 80)