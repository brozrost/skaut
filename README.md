## Installation

Clone the repository and install the project in editable mode:

```bash
git clone https://github.com/YOUR_USERNAME/skaut.git
cd skaut
python -m pip install -e .
```

Replace `YOUR_USERNAME` with the repository owner's GitHub username.

This installs the `skaut` command and makes it available from the terminal.

Verify the installation:

```bash
skaut --help
```

## Usage

By default, `skaut` prints listings priced at least 30% below the average price
of the collected listings with numeric Kč prices.

Search for listings:

```bash
skaut --category auto --query octavia
```

Show all collected listings, including listings with non-numeric or missing prices:

```bash
skaut --category auto --query octavia --all
```

`--all` skips the below-average display filter. Search filters such as
`--min-price`, `--max-price`, `--location`, `--radius`, and `--last` still apply.
When `--all` is supplied, `--below` is ignored.

Show listings from the last two calendar days:

```bash
skaut --category auto --query octavia --last 2 --all
```

`--last 1` means today, `--last 2` means today and yesterday, and so on.
The filter uses the date displayed by Bazoš and the current date in
`Europe/Prague`. The number of days must be a positive integer.

Listings need a readable date to match `--last`. The date filter is applied
before calculating the average price and saving JSON. Dates are displayed
and exported as `YYYY-MM-DD`.

Combine `--all` with a date filter, maximum price, and page limit:

```bash
skaut \
    --category mobil \
    --query 'iphone "17 pro"' \
    --max-price 30000 \
    --last 2 \
    --max-pages 100 \
    --all
```

Limit the number of pages:

```bash
skaut --category auto --query octavia --max-pages 10
```

The default limit is 5 pages. `--max-pages` sets an upper limit: scraping stops
earlier when a page contains no listings or a later page returns HTTP 404.
`--all` and `--last` use the same page limit.

Show listings priced at least 30% below the average:

```bash
skaut --category auto --query octavia --below 30
```

Use a different threshold:

```bash
skaut --category auto --query octavia --below 20
```

Only listings with numeric Kč prices are included in the average and the
below-average output. When `--last` is supplied, the average is calculated
using only listings that pass the date filter.

Filter by location and radius:

```bash
skaut \
    --category auto \
    --query octavia \
    --location Praha \
    --radius 50
```

Filter by price:

```bash
skaut \
    --category auto \
    --query octavia \
    --min-price 100000 \
    --max-price 400000
```

Add `--all` to either example to display every collected listing matching the
search filters.

Save the results to a JSON file:

```bash
skaut \
    --category auto \
    --query octavia \
    --output results.json
```

The JSON file contains all listings matching the search filters and `--last`,
including those excluded from the below-average terminal output. It works
with `--all` as well. Each listing includes a `date` field in `YYYY-MM-DD`
format, or `null` when no readable date was found.

## Command-line options

| Option | Description |
|--------|-------------|
| `--category` | Required Bazoš category (`auto`, `pc`, `mobil`, `elektro`, `foto`, `sport`, `dum`, `nabytek`, `ostatni`) |
| `--query` | Required search phrase |
| `--location` | Optional city or postal code |
| `--radius` | Search radius in kilometres (default: `25`) |
| `--min-price` | Minimum price in Kč |
| `--max-price` | Maximum price in Kč |
| `--max-pages` | Maximum number of result pages to scrape (default: `5`) |
| `--last DAYS` | Keep listings from the last positive number of calendar days, including today in Prague time. No date filter by default. |
| `--all` | Print all listings matching the search and date filters; the page limit still applies. Overrides `--below`. |
| `--below` | Print listings priced at least this percentage below the average (default: `30`). Ignored with `--all`. |
| `--delay` | Delay between requests in seconds (default: `1.0`) |
| `--output` | Save all listings matching the search and date filters to a JSON file |