# main.py
#
# Command-line interface for the Bazoš scraper.
#
# Example usage:
#
#     python main.py --category auto --query octavia
#
# Limit the number of pages:
#
#     python main.py --category auto --query octavia --max-pages 2
#
# Save results to JSON:
#
#     python main.py --category auto --query octavia --output results.json

import re
import argparse
import json

from dataclasses import asdict
from urllib.parse import urlencode

from .skaut_scraper import Listing, scrape_all_pages


# Bazoš uses separate subdomains for categories.
#
# Examples:
#     https://auto.bazos.cz/
#     https://pc.bazos.cz/
#     https://mobil.bazos.cz/
CATEGORY_DOMAINS = {
    "auto": "auto.bazos.cz",
    "pc": "pc.bazos.cz",
    "mobil": "mobil.bazos.cz",
    "elektro": "elektro.bazos.cz",
    "foto": "foto.bazos.cz",
    "sport": "sport.bazos.cz",
    "dum": "dum.bazos.cz",
    "nabytek": "nabytek.bazos.cz",
    "ostatni": "ostatni.bazos.cz",
}


def parse_arguments() -> argparse.Namespace:
    """
    Define and parse command-line arguments.

    argparse automatically generates:
    - help text,
    - validation for known options,
    - error messages for missing values.
    """

    parser = argparse.ArgumentParser(
        description="Search and scrape listings from Bazoš."
    )

    parser.add_argument(
        "--category",
        required=True,
        choices=CATEGORY_DOMAINS.keys(),
        help="Bazoš category to search.",
    )

    parser.add_argument(
        "--query",
        required=True,
        help='Search phrase, for example "octavia" or "thinkpad t14".',
    )

    parser.add_argument(
        "--location",
        help="Optional city or postal code.",
    )

    parser.add_argument(
        "--radius",
        type=int,
        default=25,
        help="Search radius in kilometres. Default: 25.",
    )

    parser.add_argument(
        "--min-price",
        type=int,
        help="Minimum price in Kč.",
    )

    parser.add_argument(
        "--max-price",
        type=int,
        help="Maximum price in Kč.",
    )

    parser.add_argument(
        "--max-pages",
        type=int,
        default=5,
        help="Maximum number of result pages to scrape.",
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between requests in seconds. Default: 1.0.",
    )

    parser.add_argument(
        "--output",
        help="Optional JSON output file.",
    )

    parser.add_argument(
        "--below",
        type=float,
        default=30.0,
        help="Print listings priced this many percent below the average. Default: 30.",
    )

    return parser.parse_args()


def build_search_url(args: argparse.Namespace) -> str:
    """
    Build a Bazoš search URL from CLI arguments.

    The Bazoš form sends search values as GET query parameters.

    Example result:

        https://auto.bazos.cz/?hledat=octavia&humkreis=25
    """

    domain = CATEGORY_DOMAINS[args.category]

    parameters = {
        "hledat": args.query,
        "humkreis": args.radius,
    }

    # Only add optional parameters when the user supplied them.
    #
    # Sending empty strings is unnecessary and makes the URL harder to read.
    if args.location:
        parameters["hlokalita"] = args.location

    if args.min_price is not None:
        parameters["cenaod"] = args.min_price

    if args.max_price is not None:
        parameters["cenado"] = args.max_price

    query_string = urlencode(parameters)

    return f"https://{domain}/?{query_string}"


def save_json(listings: list[Listing], output_path: str) -> None:
    """
    Save listings to a UTF-8 JSON file.

    asdict() converts each Listing dataclass into a normal dictionary.
    """

    data = [asdict(listing) for listing in listings]

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )


def print_summary(listings: list[Listing]) -> None:
    """
    Print a compact terminal summary.

    Full descriptions are omitted here because they make terminal output noisy.
    """

    for listing in listings:
        print(f"[{listing.id}] {listing.title}")
        print(f"Price:    {listing.price}")
        print(f"Location: {listing.location}")
        print(f"URL:      {listing.url}")
        print("-" * 80)

    print(f"Total unique listings: {len(listings)}")

def parse_price(price_text: str | None) -> int | None:
    """
    Convert a Bazoš price string into an integer number of Kč.

    Examples:
        "149 800 Kč" -> 149800
        "1 250 000 Kč" -> 1250000

    Non-numeric prices such as "Dohodou" return None.
    """

    if price_text is None:
        return None

    # Ignore prices in currencies other than Kč.
    if "Kč" not in price_text:
        return None

    digits = re.sub(r"\D", "", price_text)

    if not digits:
        return None

    return int(digits)


def print_below_average_listings(
    listings: list[Listing],
    percentage_below: float = 0.30,
) -> None:
    """
    Print listings whose price is at least the specified percentage
    below the arithmetic average.

    percentage_below=0.30 means 30% below average.
    """

    priced_listings: list[tuple[Listing, int]] = []

    for listing in listings:
        numeric_price = parse_price(listing.price)

        if numeric_price is not None:
            priced_listings.append((listing, numeric_price))

    if not priced_listings:
        print("No listings with valid numeric Kč prices were found.")
        return

    if not 0 <= percentage_below <= 1:
        raise ValueError("percentage_below must be between 0 and 1.")

    average_price = (
        sum(price for _, price in priced_listings)
        / len(priced_listings)
    )

    threshold = average_price * (1 - percentage_below)
    percentage_display = percentage_below * 100

    matching_listings = [
        (listing, price)
        for listing, price in priced_listings
        if price <= threshold
    ]

    matching_listings.sort(key=lambda item: item[1])

    print()
    print(f"Listings with numeric prices: {len(priced_listings)}")
    print(f"Average price: {average_price:,.0f} Kč")
    print(
        f"{percentage_display:g}% below average: "
        f"{threshold:,.0f} Kč"
    )
    print()
    print(
        f"Listings priced at least "
        f"{percentage_display:g}% below average:"
    )
    print("-" * 80)

    if not matching_listings:
        print("No matching listings found.")
        return

    for listing, price in matching_listings:
        difference_percentage = (
            (average_price - price) / average_price
        ) * 100

        print(listing.title)
        print(f"Price: {price:,.0f} Kč")
        print(f"Below average: {difference_percentage:.1f}%")
        print(f"URL: {listing.url}")
        print("-" * 80)

def main() -> None:
    """
    Main CLI workflow:

    1. Read arguments.
    2. Build the search URL.
    3. Run the scraper.
    4. Print results.
    5. Optionally save JSON.
    """

    args = parse_arguments()

    search_url = build_search_url(args)

    print(f"Search URL: {search_url}")

    listings = scrape_all_pages(
        start_url=search_url,
        delay=args.delay,
        max_pages=args.max_pages,
    )

    print_below_average_listings(
        listings,
        percentage_below=args.below / 100,
    )

    if args.output:
        save_json(listings, args.output)
        print(f"Saved results to: {args.output}")


if __name__ == "__main__":
    main()