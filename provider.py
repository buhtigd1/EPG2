#!/usr/bin/env python3
# provider.py
#
# Reads:  list.xml
# Creates: epg.xml
#          epg.xml.gz

import gzip
import html
from pathlib import Path
from lxml import etree

INPUT_XML = "list.xml"
OUTPUT_XML = "epg.xml"
OUTPUT_GZ = "epg.xml.gz"

TAGS_TO_PROCESS = {
    "title",
    "desc",
    "sub-title"
}

# Channel ID replacements
CHANNEL_REPLACEMENTS = {
    "TNTSports1.uk@HD": "TNT 1 - AQ",
    "TNTSports2.uk@HD": "TNT 2 - AQ",
    "TNTSports3.uk@HD": "TNT 3 - AQ",
    "TNTSports4.uk@HD": "TNT 4 - AQ",
}


def process_text(text):
    """Decode HTML entities and trim whitespace."""
    if not text:
        return text
    return html.unescape(text).strip()


def main():
    input_file = Path(INPUT_XML)

    if not input_file.exists():
        print(f"ERROR: {INPUT_XML} not found")
        return

    print(f"Parsing {INPUT_XML}...")

    tree = etree.parse(str(input_file))
    root = tree.getroot()

    text_count = 0
    channel_count = 0
    programme_count = 0

    for elem in root.iter():
        tag = elem.tag.lower() if hasattr(elem.tag, "lower") else ""

        # Decode text fields
        if tag in TAGS_TO_PROCESS and elem.text:
            elem.text = process_text(elem.text)
            text_count += 1

        # Replace channel IDs
        if tag == "channel":
            old_id = elem.get("id")
            if old_id in CHANNEL_REPLACEMENTS:
                elem.set("id", CHANNEL_REPLACEMENTS[old_id])
                channel_count += 1

        # Replace programme channel references
        elif tag == "programme":
            old_channel = elem.get("channel")
            if old_channel in CHANNEL_REPLACEMENTS:
                elem.set("channel", CHANNEL_REPLACEMENTS[old_channel])
                programme_count += 1

        if text_count % 500 == 0 and text_count > 0:
            print(f"Processed {text_count} text items...")

    print(f"Processed text fields : {text_count}")
    print(f"Replaced channel IDs  : {channel_count}")
    print(f"Replaced programmes   : {programme_count}")

    print("Saving epg.xml...")

    tree.write(
        OUTPUT_XML,
        encoding="utf-8",
        xml_declaration=True,
        pretty_print=True
    )

    print("Creating epg.xml.gz...")

    with gzip.open(OUTPUT_GZ, "wb") as gz:
        gz.write(
            etree.tostring(
                root,
                encoding="utf-8",
                xml_declaration=True,
                pretty_print=True
            )
        )

    print("DONE!")
    print(f"XML: {OUTPUT_XML}")
    print(f"GZ : {OUTPUT_GZ}")


if __name__ == "__main__":
    main()
``
