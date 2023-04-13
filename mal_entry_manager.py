import json
import os
from datetime import datetime
from typing import Any
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

class MalEntryManager:
    """Class for querying and parsing entry data from MAL API."""

    def __init__(self, client_id: str, mal_username: str):
        if not client_id or not mal_username:
            raise ValueError("client_id or mal_username is invalid")

        self.client_id = client_id
        self.mal_username = mal_username
        self.mal_api_header = { "X-MAL-CLIENT-ID": self.client_id }
        self.mal_anime_list_url = f"https://api.myanimelist.net/v2/users/{self.mal_username}/animelist"
        self.mal_anime_details_url = "https://api.myanimelist.net/v2/anime"

    def _get_mal_json_response(self, url: str) -> dict[str, Any]:
        """Returns JSON response from passed URL using MAL API header."""
        return requests.get(url, headers=self.mal_api_header).json()

    def _get_current_cour(self) -> tuple[str, int]:
        """Returns current cour data as a tuple of season and year."""
        now = datetime.now()

        match now.month:
            case 1 | 2 | 3:
                season = "winter"
            case 4 | 5 | 6:
                season = "spring"
            case 7 | 8 | 9:
                season = "summer"
            case 10 | 11 | 12:
                season = "fall"
            case _:
                raise Exception("Impossible to get month higher than 12")

        return season, now.year

    def get_entry_details(self, id: int) -> dict[str, Any]:
        """Gets more detailed info about specific entry by given Id."""
        query_params = { "fields": ["id", "title", "alternative_titles", "start_season", "status"] }
        url = f"{self.mal_anime_details_url}/{id}?{urlencode(query_params)}"
        return self._get_mal_json_response(url)

    def get_entry_list_ids(self) -> list[int]:
        """Gets a list of MAL entry Ids from user watching and plan to watch sections."""
        base_query_params = { "limit": 1000, "sort": "anime_start_date" }
        watching_query_params = { "status": "watching", **base_query_params }
        plan_to_watch_query_params = { "status": "plan_to_watch", **base_query_params }

        url = f"{self.mal_anime_list_url}?{urlencode(watching_query_params)}"
        watching_json_data = self._get_mal_json_response(url)

        url = f"{self.mal_anime_list_url}?{urlencode(plan_to_watch_query_params)}"
        plan_to_watch_json_data = self._get_mal_json_response(url)

        return [entry["node"]["id"] for entry in watching_json_data["data"] + plan_to_watch_json_data["data"]]

    def _entry_airing_filter(self, entry: dict[str, Any], season: str, year: int) -> bool:
        """Filter function to return true only for entries which are from current cour or currently airing."""
        if "start_season" not in entry:
            return False
        
        entry_season = entry["start_season"]["season"]
        entry_year = entry["start_season"]["year"]
        entry_status = entry["status"]

        return (entry_season == season and entry_year == year) or entry_status == "currently_airing"

    def get_filtered_entry_names(self, entryIds: list[int]) -> list[list[str]]:
        """Filters entries to only current season or currently airing and returns list of lists of their names."""
        season, year = self._get_current_cour()
        entries_details = [self.get_entry_details(id) for id in entryIds]

        filtered_entries_details = filter(lambda entry: self._entry_airing_filter(entry, season, year), entries_details)
        entries_names: list[list[str]] = [[entry["title"], entry["alternative_titles"]["en"], *entry["alternative_titles"]["synonyms"]] for entry in filtered_entries_details]

        return [[name for name in set(entry_names) if name] for entry_names in entries_names]

def main() -> None:
    load_dotenv()
    CLIENT_ID = os.getenv("CLIENT_ID")
    MAL_USERNAME = os.getenv("MAL_USERNAME")

    if CLIENT_ID is None or MAL_USERNAME is None:
        raise Exception("Environment file is not configured correctly")

    mal_entry_manager = MalEntryManager(CLIENT_ID, MAL_USERNAME)

    print("Querying list of user entries...")
    ids = mal_entry_manager.get_entry_list_ids()

    print("Filtering queried user entries by current season...")
    filtered_entry_names = mal_entry_manager.get_filtered_entry_names(ids)

    print("Filtered entry names list:")
    print(json.dumps(filtered_entry_names, indent=2))

if __name__ == "__main__":
    main()
