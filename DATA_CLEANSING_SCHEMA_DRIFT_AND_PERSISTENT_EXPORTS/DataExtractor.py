from lxml import html


class MarketDataExtractor:

    def extract(self, stock):
        symbol = self.extract_symbol(stock)
        price = self.extract_price(stock)
        change_percent = self.extract_change(stock)

        if not symbol or price is None or change_percent is None:
            print(f"Extraction failed for record: {symbol or 'UNKNOWN'}")
            return None

        return {
            "symbol": symbol,
            "price": price,
            "change_percent": change_percent,
        }

    def extract_symbol(self, stock):
        element = stock.select_one(".symbol")

        if element:
            return element.get_text(strip=True)

        element = stock.select_one("[data-symbol]")

        if element:
            return element.get("data-symbol")

        return None

    def extract_price(self, stock):
        element = stock.select_one(".price")

        if element:
            return self.clean_price(element.get_text(strip=True))

        xpath_result = self.xpath_extract(
            stock,
            ".//*[@data-price]/@data-price"
        )

        if xpath_result:
            return self.clean_price(xpath_result)

        for element in stock.find_all(["span", "div", "strong"]):
            text = element.get_text(strip=True)

            if "$" in text:
                return self.clean_price(text)

        return None

    def extract_change(self, stock):
        element = stock.select_one(".change")

        if element:
            return self.clean_change(element.get_text(strip=True))

        xpath_result = self.xpath_extract(
            stock,
            ".//*[@data-change]/@data-change"
        )

        if xpath_result:
            return self.clean_change(xpath_result)

        for element in stock.find_all(["span", "div"]):
            text = element.get_text(strip=True)

            if "%" in text:
                return self.clean_change(text)

        return None

    @staticmethod
    def xpath_extract(stock, expression):
        try:
            tree = html.fromstring(str(stock))
            result = tree.xpath(expression)

            if result:
                return result[0]

        except Exception:
            return None

        return None

    @staticmethod
    def clean_price(value):
        if not value:
            return None

        try:
            value = value.replace("$", "")
            value = value.replace(",", "")
            return float(value.strip())

        except ValueError:
            return None

    @staticmethod
    def clean_change(value):
        if not value:
            return None

        try:
            value = value.replace("%", "")
            value = value.replace("+", "")
            return float(value.strip())

        except ValueError:
            return None