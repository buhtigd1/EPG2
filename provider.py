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

TNT_ID_MAP = {
    "TNT 1": "TNTSports1.uk@HD",
    "TNT 2": "TNTSports2.uk@HD",
    "TNT 3": "TNTSports3.uk@HD"
}

TNT_NAME_MAP = {
    "TNTSports1.uk@HD": "TNT 1 - AQ",
    "TNTSports2.uk@HD": "TNT 2 - AQ",
    "TNTSports3.uk@HD": "TNT 3 - AQ"
}


def process_text(text):
    """Decode HTML entities and trim whitespace."""
    if not text:
        return text
    return html.unescape(text).strip()


def update_tnt_channels(root):
    """
    Update channel IDs and display names for TNT channels.
    """

    print("Updating TNT channel mappings...")

    for channel in root.findall(".//channel"):

        channel_id = channel.get("id", "")

        # Find TNT channel from display-name
        for display_name in channel.findall("display-name"):
            name = (display_name.text or "").upper()

            for key, new_id in TNT_ID_MAP.items():
                if key in name:
                    old_id = channel_id

                    # Update channel id
                    channel.set("id", new_id)

                    # Update display-name
                    display_name.text = TNT_NAME_MAP[new_id]

                    # Update programme references
                    if old_id:
                        for programme in root.findall(".//programme"):
                            if programme.get("channel") == old_id:
                                programme.set("channel", new_id)

                    print(f"{key} -> {new_id}")
                    break

    print("TNT channel updates completed.")


def main():
    input_file = Path(INPUT_XML)

    if not input_file.exists():
        print(f"ERROR: {INPUT_XML} not found")
        return

    print(f"Parsing {INPUT_XML}...")

    tree = etree.parse(str(input_file))
    root = tree.getroot()

    # Decode HTML entities
    count = 0

    for elem in root.iter():
        tag = etree.QName(elem).localname.lower()

        if tag in TAGS_TO_PROCESS and elem.text:
            elem.text = process_text(elem.text)
            count += 1

            if count % 500 == 0:
                print(f"Processed {count} items...")

    # Update TNT channels
    update_tnt_channels(root)

    print("Saving epg.xml...")

    tree.write(
        OUTPUT_XML,
        encoding="utf-8",
        xml_declaration=True,
        pretty_print=True
    )

    print("Creating epg.xml.gz...")

    with gzip.open(OUTPUT_GZ, "wb", compresslevel=6) as gz:
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
