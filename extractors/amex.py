
import re
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, field_validator
from .base import BaseExtractor

class Transaction(BaseModel):
    date: str
    description: str
    money_in: Decimal | None
    money_out: Decimal | None

    @field_validator("money_in", "money_out", mode="before")
    def validate_money(cls, v:str) -> Decimal:
        if not v:
            return None
        return Decimal(v.replace('.', "").replace(",", ".").replace(" ", "").strip())
    

    class AmexExtractor(BaseExtractor):
        PATTERN = re.compile(
        r'^(?P<date>\d{2}\.\d{2})\s+'       # first date
        r'\d{2}\.\d{2}\s+'                  # second date, ignored
        r'(?P<description>.*?)\s+'          # description
        r'(?P<money>\d{1,3}(?:\.\d{3})*,\d{2})$'  # amount in European format
    )
        
    def _find_transaction_start(lines):
        for i, line in enumerate(lines):
            if line.startswith("Saldo des laufenden Monats"):
                search_start_index = i

        tx_start_index = line[search_start_index:].index(
            "Umsatz vom Buchungsdatum Details Betrag in Fremdwährung Betrag EUR"
            )
        return search_start_index + tx_start_index
    
    def _build_transaction(match_data, lines, i):
        tx = Transaction(
            date=match_data["date"],
            description=match_data["description"],
            money_in=None,
            money_out=None
        )

        if i < len(lines) and lines[i + 1] == "GUTSCHRIFT":
            tx.money_in = match_data["money"]
            return tx, 2
        else:
            tx.money_out = match_data["money"]
            return tx, 1

        




            


