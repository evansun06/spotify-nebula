"""json reader of spotify.com api"""

# pylint: disable=line-too-long

import requests


class Reader:
    """Reader reads api data and transforms it into useable information"""

    BASE_URL = "https://api.spotify.com/"

    HEADERS = {
        "User-Agent": "tool/1.2 (username: lyanriu8; contact: Ryanliu103@gmail.com)"}

    def __init__(self, username):
        self.username = username
        self.sorted_archive = {}

    def get_base_archive(self):
        """EFFECTS: retrieves archives for given player username"""

        url = f"{self.BASE_URL}v1/users/{self.username}"

        response = requests.get(url, headers=self.HEADERS, timeout=10)

        archive = response.json()
        print(archive)
