from typing import Optional
import xml.etree.ElementTree as ET
from urllib.parse import urlencode
import requests
from colorama import Fore

from rss_feed_modifications import DEFAULT_MODIFICATION_LIST, RssEntryModification

class RssFeedManager:
    
    BASE_NYAA_URL = "https://nyaa.si/"

    RESOLUTION_PARAM = "1080p"
    EXCLUDE_BATCH_PARAM = "-batch"
    SUBBER_LIST = ["SubsPlease", "Erai-raws", "EMBER", "Anime Time", "A-L"]

    BASE_QUERY_PARAMS = { "page": "rss", "c": "1_2" }

    LOG_INDENT = "  "

    def __init__(self, modifications: list[RssEntryModification]):
        self.modifications = modifications

    def _feed_has_entries(self, rss_url: str) -> bool:
        """Checks whether RSS feed has any entries."""
        response = requests.get(rss_url)
        root = ET.fromstring(response.content)
        return len(root.findall(".//item")) > 0
    
    def _build_url(self, entry_name: str, subber: str) -> str:
        query_params = { "q": f"{entry_name} {subber} {self.RESOLUTION_PARAM} {self.EXCLUDE_BATCH_PARAM}", **self.BASE_QUERY_PARAMS }
        return f"{self.BASE_NYAA_URL}?{urlencode(query_params)}"

    def _log_found_entry(self, entry_name: str, subber: str, requires_entries: bool, modification_description: Optional[str] = None) -> None:
        intro_text = "Found RSS feed entries for:" if requires_entries else "Added default RSS feed URL:"
        print(f"{Fore.GREEN}{intro_text}{Fore.RESET}")

        print(f"{self.LOG_INDENT}Searched name: {Fore.CYAN}{entry_name}{Fore.RESET}")
        print(f"{self.LOG_INDENT}Subber: {Fore.BLUE if subber == self.SUBBER_LIST[0] else Fore.YELLOW}{subber}{Fore.RESET}")

        if modification_description:
            print(f"{self.LOG_INDENT}Modification: {Fore.YELLOW}{modification_description}{Fore.RESET}")

    def _log_not_found_entry(self, entry_names: list[str]) -> None:
        print(f"{Fore.RED}Not found any RSS feed entries for:{Fore.RESET}")
        print(f"{self.LOG_INDENT}Searched names:")
        for entry_name in entry_names:
           print(f"{self.LOG_INDENT * 2}{Fore.CYAN}{entry_name}{Fore.RESET}") 

    def get_entry_url(self, entry_names: list[str], requires_entries = True) -> Optional[str]:
        for subber in self.SUBBER_LIST:
            # Search all unmodified names first
            for entry_name in entry_names:
                url = self._build_url(entry_name, subber)

                if not requires_entries or self._feed_has_entries(url):
                    self._log_found_entry(entry_name, subber, requires_entries)
                    return url

            # Search all modifications in a row
            for modification in self.modifications:
                modified_entry_names = [modification.callback(entry_name) for entry_name in entry_names]
                flattened_modified_entry_names = [entry_name for single_entry_names in modified_entry_names for entry_name in single_entry_names]

                for entry_name in flattened_modified_entry_names:
                    url = self._build_url(entry_name, subber)

                    if not requires_entries or self._feed_has_entries(url):
                        self._log_found_entry(entry_name, subber, requires_entries, modification.description)
                        return url

        self._log_not_found_entry(entry_names)
        return None

    def get_all_entries_urls(self, entry_list_names: list[list[str]], requires_entries = True) -> list[str]:
        all_entries_urls = [self.get_entry_url(entry_names, requires_entries) for entry_names in entry_list_names]
        return [url for url in all_entries_urls if url is not None]


def main() -> None:
    test_entries = [
        [ "Vinland Saga Season 2" ],
        [ "Heavenly Delusion", "Tengoku Daimakyou" ],
        [ "Paradition", "Hell's Paradise", "Jigokuraku", "Heavenhell" ],
        [ "Kimetsu no Yaiba: Katanakaji no Sato-hen", "Demon Slayer: Kimetsu no Yaiba Swordsmith Village Arc" ],
        [ "Not-existing-stuff", "huehue: hue", "testeroni 95th season" ],
        [ "Shin no Nakama ja Nai to Yuusha no Party wo Oidasareta node, Henkyou de Slow Life suru Koto ni Shimashita 2nd", "Banished From The Hero's Party, I Decided To Live A Quiet Life In The Countryside Season 2" ],
    ]

    rss_manager = RssFeedManager(DEFAULT_MODIFICATION_LIST)
    url_list = rss_manager.get_all_entries_urls(test_entries)

    print("\nList of entry URLs:")
    for url in url_list:
        print(url)

if __name__ == "__main__":
    main()
