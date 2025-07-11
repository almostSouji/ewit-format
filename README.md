# About

Format ewit csv output to be easier to read in sequence, like a chat while extracting useful information (invite links for telegram and discord, strings matching wallet addresses).

At its core, this is a very simple, hacky, poc of a CSV formatter aligning with the export format of ewitness.


# Usage


Available template strings depend on the provided csv data, as determined by the header line. Names are used lowercase and with spaces replaced by `_`. For example, the key `SERVER NAME` is represented by the template `{server_name}`.

Additionally to the csv data, the script adds the following templates:

- `{row}` represents the message number, starting with 1 as read from the csv data (minus the header line)
- `{timestamp_fmt}` represents the timestamp (if available) in an easier to read format
- `{format_short}` represents the first letter of the platform in upper case

Messages are sorted by `"TIMESTAMP"` column ascending. So chats read from top to bottom

## Python 

```sh
python ./format.py ./ewit-export.csv
# or
./format.py ./ewit-export.csv # with chmod +x ./format.py and shebang support
```

To determine the format, modify the `FORMAT` variable in `format.py`.

Due to python format string handling, braces have to be escaped, so the template `{server_name}` has to be used as `f"{{server_name}}"` in the template string.

## Node.js

```sh
node format.js ./ewit-export.csv
```

To determine the format, modify the `FORMAT` constant in `format.js`.

