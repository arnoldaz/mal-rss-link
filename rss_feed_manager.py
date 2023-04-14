import re
import xml.etree.ElementTree as ET
from urllib.parse import urlencode

import requests
from colorama import Fore

class RssFeedManager:
    
    BASE_NYAA_URL = "https://nyaa.si/"

    RESOLUTION_PARAM = "1080p"
    EXCLUDE_BATCH_PARAM = "-batch"
    SUBBER_LIST = ["SubsPlease", "Erai-raws", "EMBER", "Anime Time", "A-L"]

    BASE_QUERY_PARAMS = { "page": "rss", "c": "1_2" }

    def __init__(self):
        pass
    
    def _feed_has_entries(self, rss_url: str) -> bool:
        """Checks whether RSS feed has any entries."""
        response = requests.get(rss_url)
        root = ET.fromstring(response.content)
        return len(root.findall(".//item")) > 0
    
    def get_entry_urls(self, entry_names: list[str], requires_entries = True) -> list[str]:
        """
        Gets entry RSS feed URL list from entry names list.

        :param list[str] entry_names: List of combined entry names.
        :param bool requires_entries: Checks RSS feed will all possible subbers and will only add URL to the list if feed has any entries.
        """
        indent = "  "
        url_list = []
        for entry_name in entry_names:
            found_url = False
            for subber in self.SUBBER_LIST:
                query_params = { "q": f"{entry_name} {self.RESOLUTION_PARAM} {self.EXCLUDE_BATCH_PARAM} {subber}", **self.BASE_QUERY_PARAMS }
                potential_url = f"{self.BASE_NYAA_URL}?{urlencode(query_params)}"

                if not requires_entries or self._feed_has_entries(potential_url):
                    if requires_entries:
                        print("Found entries for:")
                        print(f"{indent}Combined name:")
                        print(f"{indent * 2}{Fore.CYAN}{entry_name}{Fore.RESET}")
                        print(f"{indent}Subber:")
                        print(f"{indent * 2}{Fore.BLUE if subber == self.SUBBER_LIST[0] else Fore.YELLOW}{subber}{Fore.RESET}")
                    else:
                        print("Added URL with default subber:")
                        print(f"{indent}Combined name:")
                        print(f"{indent * 2}{Fore.CYAN}{entry_name}{Fore.RESET}")
                        print(f"{indent}Subber:")
                        print(f"{indent * 2}{Fore.BLUE}{subber}{Fore.RESET}")

                    url_list.append(potential_url)
                    found_url = True
                    break
            
            if not found_url:
                print(f"{Fore.RED}Not found any entries for:{Fore.RESET}")
                print(f"{indent}Combined name:")
                print(f"{indent * 2}{Fore.CYAN}{entry_name}{Fore.RESET}")

        return url_list
        
    def format_entry_names_list(self, entries_names: list[list[str]]) -> list[str]:
        """Combines all names for each entry into single string by wrapping it in parentheses and dividing them with vertical bars."""
        return ["|".join([f"({name})" for name in entry_names]) for entry_names in entries_names]

    def extend_entry_names_list(self, entries_names: list[list[str]]) -> list[list[str]]:
        """Extends names list for each entry by reformating already existing names to cover more various subber naming schemes."""
        extended_entries_names = []

        for entry_names in entries_names:
            additional_entry_names = []

            for entry_name in entry_names:
                # Postfix after colon is not always used in naming, additionally add only part before colon
                if ":" in entry_name:
                    first_part, _ = entry_name.split(":")
                    additional_entry_names.append(first_part)
                
                # Remove all instances of word "season" with a number afterwards
                additional_entry_names.append(re.sub(r"\s*season\s*[0-9]+\s*", "", entry_name, flags=re.IGNORECASE))

                # Remove all instances of word "season" with ordinal number prefix
                additional_entry_names.append(re.sub(r"\s*[0-9]*[st|nd|rd|th]+\s*season\s*", "", entry_name, flags=re.IGNORECASE))

                # Remove all punctuation
                additional_entry_names.append(re.sub(r"[^\w\s]", "", entry_name))

            extended_entries_names.append(list(set(entry_names + additional_entry_names)))

        return extended_entries_names

def main() -> None:
    test_entries = [
        [ "Vinland Saga Season 2" ],
        [ "Heavenly Delusion", "Tengoku Daimakyou" ],
        [ "Paradition", "Hell's Paradise", "Jigokuraku", "Heavenhell" ],
        [ "Kimetsu no Yaiba: Katanakaji no Sato-hen", "Demon Slayer: Kimetsu no Yaiba Swordsmith Village Arc" ],
        [ "Not-existing-stuff", "huehue: hue", "testeroni 95th season" ]
    ]

    rss_manager = RssFeedManager()
    extended_entries_names = rss_manager.extend_entry_names_list(test_entries)
    formatted_entry_names = rss_manager.format_entry_names_list(extended_entries_names)
    url_list = rss_manager.get_entry_urls(formatted_entry_names)

    print("List of entry URLs:")
    for url in url_list:
        print(url)

if __name__ == "__main__":
    main()
