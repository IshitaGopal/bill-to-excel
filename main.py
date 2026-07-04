import argparse
from pathlib import Path

import pandas as pd
import pdfplumber
from loguru import logger

from extractors.amex import AmexExtractor
from extractors.revolut import RevolutExtractor


def convert_pdf(path_input_pdf):
    # 1. Read PDF
    logger.info("Reading pdf")
    with pdfplumber.open(path_input_pdf) as pdf:
        text = (pdf.pages[0].extract_text() or "")[:100]

    text_lower = text.lower()

    # 2. Detect which bank
    if "revolut" in text_lower:
        logger.info("Loading Revolut Converter")
        extractor = RevolutExtractor()
    elif "american express" in text_lower:
        logger.info("Loading Amex Converter")
        extractor = AmexExtractor()
    else:
        raise ValueError(f"Could not detect bank type from PDF: {path_input_pdf}")

    # 3. Extract transactions
    logger.info("Extracting transactions")
    transactions = extractor.extract_transactions(path_input_pdf)

    # 4. Convert to DataFrame
    logger.info("Converting to a Dataframe")
    data = [t.model_dump() for t in transactions]
    df = pd.DataFrame(data)

    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_file_name",
        help="file name for the pdf you want to convert",
        type=str,
    )
    parser.add_argument(
        "-idir",
        "--input_dir",
        help="path for the input directory",
        default="data/input",
    )
    parser.add_argument(
        "-odir",
        "--output_dir",
        help="path for the output directory",
        default="data/output",
    )

    args = parser.parse_args()

    input_file_name = args.input_file_name
    input_dir = args.input_dir
    output_dir = args.output_dir

    input_path = Path(input_dir) / input_file_name
    output_path = Path(output_dir) / Path(input_file_name).with_suffix(".xlsx")

    if not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = convert_pdf(input_path)
    df.to_excel(output_path, index=False)
    logger.info(f"Saved to {output_path}")
