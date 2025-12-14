from abc import abstractmethod
from typing import List, Optional
import pdfplumber

class BaseExtractor:
    PATTERN = None

    def _get_all_lines(self, pdf_file):
            all_lines = []
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    text = page.extract_text() or ""
                    all_lines.extend(text.split("\n"))
            return all_lines
    

    def _try_pattern(self, line: str) -> dict | None:
        match = self.PATTERN.search(line)
        if not match:
            return None
        return match.groupdict()

    @abstractmethod
    def _find_transaction_start(self, lines: List[str]) -> int | None:
        pass

    @abstractmethod
    def _build_transaction():
        pass

    def extract_transactions(
        self,
        pdf: Optional[str] = None,
        lines: Optional[List[str]] = None
    ):

        if pdf is None and lines is None:
            raise ValueError("Provide either pdf or lines")

        if lines is None:
            lines = self._get_all_lines(pdf)

        transactions = []
        start = self._find_transaction_start(lines)

        if start is None:
            return transactions

        i = start + 1
        while i < len(lines):
            match_data = self._try_pattern(lines[i])

            if match_data:
                tx, consumed = self._build_transaction(match_data, lines, i)
                transactions.append(tx)
                i += consumed
            else:
                i += 1

        return transactions
    
        


