import argparse
import os
import sys

from dotenv import load_dotenv
from colorama import just_fix_windows_console, Fore
import pyperclip

from mal_entry_manager import MalEntryManager
from rss_feed_manager import RssFeedManager

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="MAL RSS link", description="Creates list of RSS URLs based on MAL user entry lists.")
    parser.add_argument("-i", "--ignore-feed", action="store_true", help="disables checking if entries exist in feed and will return RSS feed URLs with default subber")
    parser.add_argument("-s", "--season", choices=["winter", "spring", "summer", "fall"], help="season of specific cour to be filtered by, must be defined together with year; defaults to current cour if not defined")
    parser.add_argument("-y", "--year", type=int, help="year of specific cour to be filtered by, must be defined together with season; defaults to current cour if not defined")

    args = parser.parse_args()

    if (args.season and not args.year) or (not args.season and args.year):
        parser.error("Both season (--season) and year (--year) parameters must be specified or not specified together")
    
    if args.year and (args.year < 1970 or args.year > 2050):
        parser.error("Year (--year) parameter is not a valid year")
    
    return args

def initialize():
    # Fix ANSI escapes on cmd for colors to work
    just_fix_windows_console()

    # Load environment variables
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    mal_username = os.getenv("MAL_USERNAME")

    if not client_id:
        print("Error: CLIENT_ID is not configured in environment file")
        sys.exit(0)

    if not mal_username:
        print("Error: MAL_USERNAME is not configured in environment file")
        sys.exit(0)

    return client_id, mal_username

def main() -> None:
    args = parse_arguments()
    client_id, mal_username = initialize()

    mal_entry_manager = MalEntryManager(client_id, mal_username)
    entry_list_ids = mal_entry_manager.get_entry_list_ids()
    entries_names = mal_entry_manager.get_filtered_entry_names(entry_list_ids, (args.season, args.year))

    rss_feed_manager = RssFeedManager()
    extended_entries_names = rss_feed_manager.extend_entry_names_list(entries_names)
    formatted_entry_names = rss_feed_manager.format_entry_names_list(extended_entries_names)
    url_list = rss_feed_manager.get_entry_urls(formatted_entry_names, not args.ignore_feed)

    combined_url_text = "\n".join(url_list)
    print("\nFinal URL list:")
    print(f"{Fore.GREEN}{combined_url_text}{Fore.RESET}")

    pyperclip.copy(combined_url_text)
    print("\nURL list has been copied to the clipboard!")

if __name__ == "__main__":
    main()

