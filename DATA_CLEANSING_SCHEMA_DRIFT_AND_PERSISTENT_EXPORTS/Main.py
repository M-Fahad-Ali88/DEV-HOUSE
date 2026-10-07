from bs4 import BeautifulSoup

from DataExtractor import MarketDataExtractor
from DataValidator import MarketRecord
from Exporter import export_data


HTML = """
<html>
    <body>
        <div class="stock">
            <span class="symbol">AAPL</span>
            <span class="price">$245.20</span>
            <span class="change">+1.25%</span>
        </div>

        <div class="stock">
            <span class="symbol">MSFT</span>
            <div data-price="510.30"></div>
            <span class="change">-0.42%</span>
        </div>

        <div class="stock">
            <span class="symbol">NVDA</span>
            <div class="market-info">
                <strong>$180.50</strong>
            </div>
            <span class="change">+2.10%</span>
        </div>
    </body>
</html>
"""


def main():
    soup = BeautifulSoup(HTML, "html.parser")

    extractor = MarketDataExtractor()
    records = []

    for stock in soup.select(".stock"):
        data = extractor.extract(stock)

        if data is None:
            continue

        try:
            record = MarketRecord(**data)
            records.append(record.model_dump())

        except Exception as error:
            print(f"Validation failed: {error}")

    export_data(records)

    print(f"\nSuccessfully exported {len(records)} records.")


if __name__ == "__main__":
    main()