#!/usr/bin/env python3

import argparse
import re
import sys
from datetime import datetime

if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1)

parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter, description=__doc__
)
parser.add_argument("file", help="path to the CSV file to parse")
parser.add_argument(
    "-f",
    "--format",
    help="output format expression",
    default="{DARK_GRAY}{row} [{platform_short}] {BRIGHT_GREEN}{server_name} {LIGHT_GRAY}{timestamp_fmt} {BRIGHT_MAGENTA}{username}{RESET}: {message}",
    required=False,
)
parser.add_argument(
    "--nosort",
    help="stick to the original sort order",
    action="store_true",
    required=False,
)
parser.add_argument(
    "--invites",
    help="[EXPERIMENTAL] parse potential telegram and discord invites from message content",
    action="store_true",
    required=False,
)
parser.add_argument(
    "--wallets",
    help="[EXPERIMENTAL] parse potential wallet addresses from message content",
    action="store_true",
    required=False,
)
parser.add_argument(
    "--dedupe",
    help="Dedupe messages based on content",
    action="store_true",
    required=False,
)
parser.add_argument(
    "--no-color",
    help="Remove colors (useful for exporting to file)",
    action="store_true",
    required=False,
)

args = parser.parse_args()
config = vars(args)

# ---------------

colors = {
    "BLACK": "\033[30m",
    "RED": "\033[31m",
    "GREEN": "\033[32m",
    "YELLOW": "\033[33m",  # orange on some systems
    "BLUE": "\033[34m",
    "MAGENTA": "\033[35m",
    "CYAN": "\033[36m",
    "LIGHT_GRAY": "\033[37m",
    "DARK_GRAY": "\033[90m",
    "BRIGHT_RED": "\033[91m",
    "BRIGHT_GREEN": "\033[92m",
    "BRIGHT_YELLOW": "\033[93m",
    "BRIGHT_BLUE": "\033[94m",
    "BRIGHT_MAGENTA": "\033[95m",
    "BRIGHT_CYAN": "\033[96m",
    "WHITE": "\033[97m",
    "RESET": "\033[0m",  # called to return to standard terminal text color,
}

# ---------------


formatstring = config.get("format")
file = config.get("file")

assert file is not None
assert formatstring is not None

lines = open(file, encoding="utf-8-sig").readlines()
header, *lines = lines

header = [
    x.strip().lstrip('"').rstrip('"').replace(" ", "_").lower()
    for x in header.split(",")
]

n_attributes = len(header)
attributes = [attribute.lower() for attribute in header]

pattern = ",".join(f'\\"(?P<{x}>[^\\"]*?)\\"' for x in attributes)

messages = []

reg = re.compile(pattern)
for num, entry in enumerate(re.findall(reg, "\n".join(lines))):
    message = dict()
    message["row"] = num + 1

    for name, value in zip(header, entry):
        if name == "timestamp":
            message["timestamp_fmt"] = datetime.fromisoformat(value).strftime(
                "%Y-%m-%d %H:%M"
            )

        if name == "platform":
            message["platform_short"] = value[0].upper()
        message[name] = value

    messages.append(message)


def sortabletime(time: str):
    dt = datetime.fromisoformat(time)
    return (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)


patterns = {
    "BTC": re.compile(r"(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}"),
    "ETH": re.compile(r"0x[a-fA-F0-9]{40}"),  # ETH etc. ERC-20
    "DASH": re.compile(r"X[1–9A-HJ-NP-Za-km-z]{33}"),
    "XMR": re.compile(r"[48][0–9AB][1–9A-HJ-NP-Za-km-z]{93}"),
    "ADA": re.compile(r"addr1[a-z0–9]"),
    "ATOM": re.compile(r"cosmos[a-zA-Z0–9_.-]{10,}"),
    "DOGE": re.compile(r"\sD[a-zA-Z0–9_.-]{33}"),
    "LTC": re.compile(r"[LM3][a-km-zA-HJ-NP-Z1–9]{26,33}"),
    "NEM": re.compile(r"[N][A-Za-z0–9-]{37,52}"),
    "NEO": re.compile(r"N[0–9a-zA-Z]{33}"),
    "ONT": re.compile(r"A[0–9a-zA-Z]{33}"),
    "DOT": re.compile(r"1[0–9a-zA-Z]{47}"),
    "XRP": re.compile(r"r[0–9a-zA-Z]{33}"),
    "XLM": re.compile(r"G[0–9A-Z]{40,60}"),
}


def find_wallets(text: str):
    matches = dict()
    for wallet_type, pattern in patterns.items():
        for address in re.findall(pattern, text):
            matches[address] = wallet_type

    return matches


wallets = dict()
invites = set()

no_color = config.get("no_color")

if not config.get("nosort"):
    messages.sort(key=lambda x: sortabletime(x["timestamp"]))

seen = set()
for message in messages:
    out = formatstring

    content = message.get("message", "")
    h = hash(content)

    if config.get("dedupe"):
        if h in seen:
            continue
        else:
            seen.add(h)

    wallets.update(find_wallets(content))

    pattern = re.compile(r"t\.me\/\S*|\.gg\/\S*", flags=re.IGNORECASE)
    for invite in re.findall(pattern, content):
        invites.add(invite)

    pattern = re.compile(r"{(.+?)}")
    for placeholder in re.findall(pattern, out):
        field_value = message.get(placeholder, None)
        color_replacer = colors.get(placeholder, None)

        if field_value is not None:
            value = field_value
        elif color_replacer is not None:
            value = "" if no_color else color_replacer
        else:
            value = "-"

        if placeholder == "row":
            out = out.replace("{row}", str(value).rjust(len(str(len(messages))), " "))
        else:
            out = out.replace(f"{{{placeholder}}}", str(value))

    print(out)

if config.get("invites"):
    if not no_color:
        print(colors.get("RESET"), file=sys.stderr)
    print("# Found Invites:" if len(invites) else "# Found no invites", file=sys.stderr)
    print("\n".join([f"- {invite}" for invite in invites]), file=sys.stderr)

if config.get("wallets"):
    if not no_color:
        print(colors.get("RESET"), file=sys.stderr)
    print(
        (
            "# Found potential wallet addresses:"
            if len(wallets)
            else "# Found no potential wallet addresses"
        ),
        file=sys.stderr,
    )
    for address, wallet_type in wallets.items():
        print(f"- [{wallet_type}] {address}", file=sys.stderr)

if config.get("dedupe"):
    print("\n\n")
    if not no_color:
        print(colors.get("RED"), file=sys.stderr)
    warnstring = (
        "!!! Executed with --dedupe, potentially multiple authors per message !!!"
    )
    print(
        "".join(
            [
                "!" * len(warnstring) + "\n",
                warnstring + "\n",
                "!" * len(warnstring) + "\n",
                "" if no_color else colors.get("RESET", ""),
            ]
        ),
        file=sys.stderr,
    )
