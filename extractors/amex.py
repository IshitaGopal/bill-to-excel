import re
from decimal import Decimal

from pydantic import BaseModel, field_validator

from extractors.base import BaseExtractor


class Transaction(BaseModel):
    date: str
    description: str
    money_in: Decimal | None
    money_out: Decimal | None

    @field_validator("money_in", "money_out", mode="before")
    def validate_money(cls, v):
        if v is None or v == "":
            return None

        if isinstance(v, str):
            v = v.replace(".", "").replace(",", ".").replace(" ", "").strip()

        return Decimal(v)


class AmexExtractor(BaseExtractor):
    PATTERN = re.compile(
        r"^(?P<date>\d{2}\.\d{2})\s+"  # first date
        r"\d{2}\.\d{2}\s+"  # second date, ignored
        r"(?P<description>.*?)\s+"  # description
        r"(?P<money>\d{1,3}(?:\.\d{3})*,\d{2})$"  # amount in European format
    )

    def _find_transaction_start(self, lines):
        search_start_index = None
        for i, line in enumerate(lines):
            if line.startswith("Saldo des laufenden Monats"):
                search_start_index = i
                break

        if search_start_index is None:
            raise ValueError("Transaction start line not found")

        tx_start_index = lines[search_start_index:].index(
            "Umsatz vom Buchungsdatum Details Betrag in Fremdwährung Betrag EUR"
        )
        return search_start_index + tx_start_index

    def _build_transaction(self, match_data, lines, i):
        money_in = None
        money_out = None

        if i + 1 < len(lines) and lines[i + 1] == "GUTSCHRIFT":
            money_in = match_data["money"]
            consumed = 2
        else:
            money_out = match_data["money"]
            consumed = 1

        tx = Transaction(
            date=match_data["date"],
            description=match_data["description"],
            money_in=money_in,
            money_out=money_out,
        )
        return tx, consumed
