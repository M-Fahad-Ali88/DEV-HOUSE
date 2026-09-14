from bs4 import BeautifulSoup


class StockTableExtractor:
    """
    Extracts stock pricing data from a static HTML table.
    """

    def extract(self, html: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")

        table = soup.select_one("table.stock-data")

        if table is None:
            return []

        rows = table.select("tbody tr")

        stocks = []

        for row in rows:
            cells = row.select("td")

            if not cells:
                continue

            symbol = self._get_cell_text(cells, 0)
            company = self._get_cell_text(cells, 1)
            price = self._get_cell_text(cells, 2)
            change = self._get_cell_text(cells, 3)

            stocks.append(
                {
                    "symbol": symbol,
                    "company": company,
                    "price": price,
                    "change": change,
                }
            )

        return stocks

    @staticmethod
    def _get_cell_text(cells, index: int):
        """
        Safely extracts text from a table cell.

        Returns None when the requested cell does not exist.
        """
        if index >= len(cells):
            return None

        text = cells[index].get_text(" ", strip=True)

        return text if text else None