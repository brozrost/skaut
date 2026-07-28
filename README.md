## Installation

Clone the repository and install the project in editable mode:

```bash
git clone https://github.com/YOUR_USERNAME/skaut.git
cd skaut
python -m pip install -e .
```

This installs the `skaut` command and makes it available from the terminal.

Verify the installation:

```bash
skaut --help
```

## Usage

Search for listings:

```bash
skaut --category auto --query octavia
```

Limit the number of pages:

```bash
skaut --category auto --query octavia --max-pages 10
```

Show listings priced at least 30% below the average:

```bash
skaut --category auto --query octavia --below 30
```

Use a different threshold:

```bash
skaut --category auto --query octavia --below 20
```

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

Save the results to a JSON file:

```bash
skaut \
    --category auto \
    --query octavia \
    --output results.json
```

## Command-line options

| Option | Description |
|--------|-------------|
| `--category` | Bazoš category (`auto`, `pc`, `mobil`, `elektro`, `foto`, `sport`, `dum`, `nabytek`, `ostatni`) |
| `--query` | Search phrase |
| `--location` | Optional city or postal code |
| `--radius` | Search radius in kilometres (default: `25`) |
| `--min-price` | Minimum price in Kč |
| `--max-price` | Maximum price in Kč |
| `--max-pages` | Maximum number of result pages to scrape (default: `5`) |
| `--below` | Print listings priced at least this percentage below the average (default: `30`) |
| `--delay` | Delay between requests in seconds (default: `1.0`) |
| `--output` | Save scraped listings to a JSON file |