# About

Format ewit csv output to be easier to read in sequence, like a chat.

At its core, this is a very simple, hacky, poc of a CSV formatter aligning with the export format of ewitness.

# Usage

```sh
cat ewit-export.csv | python3 ./format.py
# or
cat ewit-export.csv | ./format.py # with chmod +x ./format.py and shebang support
```

To determine the format, modify the `FORMAT` variable in `format.py`.

Available template strings depend on the provided csv data, as determined by the header line. Names are used lowercase and with spaces replaced by `_`. The key `SERVER NAME` is represented by the template `{server_name}`. Due to python format string handling, braces have to be escaped, making it `f"{{server_name}}"` in the template string itself.

As addition the script provides the templates:

- `{row}` represents the message number, starting with 1 as read from the csv data (minus the header line)
- `{timestamp_fmt}` represents the timestamp (if available) in an easier to read format

Messages are sorted by `"TIMESTAMP"` column ascending. 

