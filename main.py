import json
import requests
import argparse

import xml.etree.ElementTree as ET


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ignore-feed-entries", action="store_true", help="Won't check if entries exist and will return RSS feed URLs with default subber")

    args = parser.parse_args()
    
    # TODO: combine all functionality
    print(args)


if __name__ == "__main__":
    main()

