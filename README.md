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
`--min-price`, `--max-price`, `--location`, and `--radius` still apply.
When `--all` is supplied, `--below` is ignored.

Combine `--all` with a maximum price and page limit:

```bash
skaut \
    --category mobil \
    --query 'iphone "17 pro"' \
    --max-price 30000 \
    --max-pages 100 \
    --all
```

Limit the number of pages:

```bash
skaut --category auto --query octavia --max-pages 10
```

The default limit is 5 pages. `--max-pages` sets an upper limit: scraping stops
earlier when a page contains no listings or a later page returns HTTP 404.
`--all` uses the same page limit.

Show listings priced at least 30% below the average:

```bash
skaut --category auto --query octavia --below 30
```

Use a different threshold:

```bash
skaut --category auto --query octavia --below 20
```

Only listings with numeric Kč prices are included in the average and the
below-average output.

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

The JSON file always contains all collected listings, including those excluded
from the below-average terminal output. It works with `--all` as well.

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
| `--all` | Print all collected listings; search filters and the page limit still apply. Overrides `--below`. |
| `--below` | Print listings priced at least this percentage below the average (default: `30`). Ignored with `--all`. |
| `--delay` | Delay between requests in seconds (default: `1.0`) |
| `--output` | Save all collected listings to a JSON file |
