import re
from typing import Callable, NamedTuple

RssEntryModificationCallback = Callable[[str], list[str]]

class RssEntryModification(NamedTuple):
    callback: RssEntryModificationCallback
    description: str

def split_colon_modification(entry_name: str) -> list[str]:
    modified_entries: list[str] = []

    # Remove all punctuations
    cleaned_entry_name = re.sub(r"[^\w\s]", "", entry_name)
    if cleaned_entry_name != entry_name:
        modified_entries.append(cleaned_entry_name)

    # Postfix after colon is not always used in naming, additionally add only part before colon
    if ":" in entry_name:
        first_part, _ = entry_name.split(":", 1)
        modified_entries.append(first_part)

    # Similar to colon, comma could also be used like that
    if "," in entry_name:
        first_part, _ = entry_name.split(",", 1)
        modified_entries.append(first_part)

    return modified_entries

def season_number_modification(entry_name: str) -> list[str]:
    modified_entries: list[str] = []

    # Remove all instances of word "season" or "stage" with a number afterwards
    cleaned_entry_name = re.sub(r"\s*(season|stage)\s*[0-9]+\s*", "", entry_name, flags=re.IGNORECASE)
    if cleaned_entry_name != entry_name:
        modified_entries.append(cleaned_entry_name)

    # Remove all instances of word "season" or "stage" with ordinal number prefix
    cleaned_entry_name = re.sub(r"\s*[0-9]*[st|nd|rd|th]+\s*(season|stage)\s*", "", entry_name, flags=re.IGNORECASE)
    if cleaned_entry_name != entry_name:
        modified_entries.append(cleaned_entry_name)

    return modified_entries

def starting_words_modification(entry_name: str) -> list[str]:
    modified_entries: list[str] = []

    # Take first 3 words (might be used if name is too long)
    cleaned_entry_name = " ".join(entry_name.split()[:3])
    if cleaned_entry_name != entry_name:
        modified_entries.append(cleaned_entry_name)

    # Take first 2 words after the 3 to prioritize longer name first
    cleaned_entry_name = " ".join(entry_name.split()[:2])
    if cleaned_entry_name != entry_name:
        modified_entries.append(cleaned_entry_name)

    return modified_entries

DEFAULT_MODIFICATION_LIST: list[RssEntryModification] = [
    RssEntryModification(split_colon_modification, "Removed punctuations and text after the colon"),
    RssEntryModification(season_number_modification, "Removed season numbers"),
    RssEntryModification(starting_words_modification, "Take only 2 or 3 starting words"),
] 

if __name__ == "__main__":
    # Nothing atm
    pass

