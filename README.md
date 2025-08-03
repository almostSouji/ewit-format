# About

Format ewitness csv output to be easier to read in sequence, like a chat while extracting useful information (invite links for telegram and discord, strings matching wallet addresses).

At its core, this is a very simple, hacky, poc of a CSV formatter aligning with the export format of ewitness.

# Usage

## Running the script

```sh
python ./format.py ./ewit-export.csv
# or
./format ./ewit-export.csv # with chmod +x ./format.py

```

> [!NOTE]
> Messages are sorted by timestamp ascending, so they read like a regular chat conversation from top to bottom. If you want to stick to the original sorting, use the `--nosort` flag.

## Custom format

The script supports a `-f` or `--format` flag value to use a custom format string.

Available templates depend on the provided CSV data, as determined by the header line. Names are used lowercase and with spaces replaced by `_`. For example, the key `SERVER NAME` is represented by the template `{server_name}`.

### Additional template strings

Additionally to the csv data, the script adds the following templates:

- `{row}` represents the message number, starting with 1 as read from the csv data (minus the header line)
- `{timestamp_fmt}` represents the timestamp (if available) in an easier to read format
- `{format_short}` represents the first letter of the platform in upper case

### Styling

The script exposes the following templates for styling. `{RESET}` can be used to end a styled section. As CSV data fields are always transformed to `lower_case`, colors are always used as `UPPER_CASE` templates. The following colors are available:

- `{BLACK}`
- `{RED}`
- `{GREEN}`
- `{YELLOW}`
- `{BLUE}`
- `{MAGENTA}`
- `{CYAN}`
- `{LIGHT_GRAY}`
- `{DARK_GRAY}`
- `{BRIGHT_RED}`
- `{BRIGHT_GREEN}`
- `{BRIGHT_YELLOW}`
- `{BRIGHT_BLUE}`
- `{BRIGHT_MAGENTA}`
- `{BRIGHT_CYAN}`
- `{WHITE}`
- `{RESET}`

## Default format

If `-f` or `--format` are not supplied, the script uses the following formatting by default:

```
"{DARK_GRAY}{row} [{platform_short}] {BRIGHT_GREEN}{server_name} {LIGHT_GRAY}{timestamp_fmt} {BRIGHT_MAGENTA}{username}{RESET}: {message}"
```

## Experimental

> [!TIP]
> Output for experimental flags happens at the end and is printed to standard error (stderr) for easier filtering.

### `--invites`

Try to extract telegram and discord invites from message content.

### `--wallets`

Try to extract wallet addresses based on regular expressions.

