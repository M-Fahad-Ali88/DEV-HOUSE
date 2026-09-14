from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests


class RobotsChecker:
    """
    Checks whether a URL can be crawled according to robots.txt.
    """

    def __init__(
        self,
        user_agent: str = "DistributedFinancialEngine/1.0",
    ):
        self.user_agent = user_agent
        self.parsers = {}

    def _get_parser(self, url: str) -> RobotFileParser:
        parsed_url = urlparse(url)

        robots_url = (
            f"{parsed_url.scheme}://"
            f"{parsed_url.netloc}/robots.txt"
        )

        # Reuse parser if this domain was already checked.
        if robots_url in self.parsers:
            return self.parsers[robots_url]

        parser = RobotFileParser()

        try:
            response = requests.get(
                robots_url,
                headers={
                    "User-Agent": self.user_agent
                },
                timeout=10,
            )

            if response.status_code == 200:
                parser.parse(response.text.splitlines())
            else:
                parser.parse([])

        except requests.RequestException:
            parser.parse([])

        self.parsers[robots_url] = parser

        return parser

    def can_fetch(self, url: str) -> bool:
        parser = self._get_parser(url)

        return parser.can_fetch(
            self.user_agent,
            url,
        )