
import re
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, field_validator
from extractors.base import BaseExtractor

class Transaction(BaseModel):
    date: str
    description: str
    money_in: Decimal | None
    money_out: Decimal | None
    balance: Decimal

    @field_validator("money_in", "money_out", "balance", mode="before")
    def validate_money(cls, v:str) -> Decimal:
        if not v:
            return None
        return Decimal(v.replace('€', "").replace(",", "").strip())
    

class RevolutExtractor(BaseExtractor):
    PATTERN = re.compile(
        r'^(?P<date>[A-Z][a-z]{2} \d{1,2}, 202\d)\s+'
        r'(?P<description>.+?)(?=\s*€\d)\s+'
        r'(?P<money>€\s?\d+(?:,\d{3})*\.\d{2})\s+'
        r'(?P<balance>€\s?\d+(?:,\d{3})*\.\d{2})$'
    )

    def _find_transaction_start(self, lines):
        return lines.index("Date Description Money out Money in Balance")
    
    def _build_transaction(self, match_data, lines, i):
        money_in = None
        money_out = None

        if i + 1 < len(lines) and lines[i + 1].startswith("From"):
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
            balance=match_data["balance"]
        )
        return tx, consumed