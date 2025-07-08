#!/usr/bin/env python3

import sys
import re
from datetime import datetime

# ---------------

BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"  # orange on some systems
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
LIGHT_GRAY = "\033[37m"
DARK_GRAY = "\033[90m"
BRIGHT_RED = "\033[91m"
BRIGHT_GREEN = "\033[92m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_BLUE = "\033[94m"
BRIGHT_MAGENTA = "\033[95m"
BRIGHT_CYAN = "\033[96m"
WHITE = "\033[97m"

RESET = "\033[0m"  # called to return to standard terminal text color

# ---------------

FORMAT = f"{DARK_GRAY}{{row}} {BRIGHT_GREEN}{{server_name}} {LIGHT_GRAY}{{timestamp_fmt}} {BRIGHT_MAGENTA}{{username}}{RESET}: {{message}}"

file_name = sys.argv[1]

lines = open(file_name, encoding="utf-8-sig").readlines()
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
        message[name] = value

    messages.append(message)


def sortabletime(time: str):
    dt = datetime.fromisoformat(time)
    return (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)


messages.sort(key=lambda x: sortabletime(x["timestamp"]))
for message in messages:
    out = FORMAT

    pattern = re.compile(r"{(.+?)}")
    for placeholder in re.findall(pattern, out):
        value = message.get(placeholder, "-")
        out = out.replace(f"{{{placeholder}}}", str(value))

    print(out)
