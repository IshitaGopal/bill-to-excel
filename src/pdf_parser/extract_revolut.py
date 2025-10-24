import pdfplumber
import numpy as np
import re

date_pattern = re.compile(r"^[A-Z][a-z]{2} \d{1,2}, 202\d")
euro_pattern = re.compile(r"€ ?(\d{1,3}(?:,\d{3})*\.\d{2})")


def extract_transaction_lines(page_lines):
    try:
        transaction_start = page_lines.index(
            "Date Description Money out Money in Balance"
        )
    except ValueError:
        return []  # no transactions on this page

    return [
        (i, line)
        for i, line in enumerate(page_lines[transaction_start + 1 :])
        if date_pattern.match(line) and euro_pattern.search(line)
    ]


def parse_transaction_line(transcation_line, all_lines):
    line = transcation_line[1]
    line_split = line.split()

    idx = transcation_line[0]

    date = " ".join(line_split[:3])
    description = " ".join(line_split[3:-2])
    balance = line_split[-1]
    money_in = np.nan
    money_out = np.nan

    next_line = all_lines[idx + 1] if idx + 1 < len(all_lines) else ""
    if next_line.startswith("From"):
        money_in = line_split[-2]
    else:
        money_out = line_split[-2]

    return {
        "Date": date,
        "Description": description,
        "Money Out": money_out,
        "Money In": money_in,
        "Balance": balance,
    }


def extract_payments(file):
    all_results = []
    pdf = pdfplumber.open(file)

    for page in pdf.pages:
        page_text = page.extract_text()
        page_lines = page_text.split("\n")

        transaction_lines = extract_transaction_lines(page_lines)

        for line in transaction_lines:
            result = parse_transaction_line(line, page_lines)
            if result:
                all_results.append(result)

    return all_results
