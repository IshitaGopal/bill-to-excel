# bill-to-excel

A CLI tool to convert bank/card statement PDFs into Excel files. Automatically
detects the statement type and extracts transactions for:

1. Revolut
2. Amex

## Project Structure

```
bill-to-excel/
├── extractors/
│   ├── base.py          # Shared extractor interface
│   ├── amex.py          # Amex extraction logic
│   └── revolut.py       # Revolut extraction logic
├── main.py              # CLI entry point
├── data/
│   ├── input/           # Put source PDFs here
│   └── output/          # Excel files are written here
└── pyproject.toml       # Project dependencies (managed with uv)
```

## Setup

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
uv sync
```

## Usage

Place the PDF you want to convert in `data/input/` (or anywhere, and pass
`--input_dir`), then run:

```bash
uv run main.py <input_file_name>
```

### Examples

Convert `statement.pdf` from `data/input/` to `data/output/statement.xlsx`:

```bash
uv run main.py statement.pdf
```

Specify a custom input directory:

```bash
uv run main.py statement.pdf --input_dir path/to/pdfs
```

Specify a custom output directory:

```bash
uv run main.py statement.pdf --output_dir path/to/excel_files
```

### Arguments

| Argument | Flag | Default | Description |
|---|---|---|---|
| `input_file_name` | (positional) | — | Name of the PDF file to convert |
| `--input_dir` | `-idir` | `data/input` | Directory containing the input PDF |
| `--output_dir` | `-odir` | `data/output` | Directory to write the output Excel file |

The output file is saved with the same name as the input, with a `.xlsx` extension.
