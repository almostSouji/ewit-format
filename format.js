import { readFileSync } from "node:fs";

// ---------------

const BLACK = "\x1b[30m";
const RED = "\x1b[31m";
const GREEN = "\x1b[32m";
const YELLOW = "\x1b[33m"; // orange on some systems
const BLUE = "\x1b[34m";
const MAGENTA = "\x1b[35m";
const CYAN = "\x1b[36m";
const LIGHT_GRAY = "\x1b[37m";
const DARK_GRAY = "\x1b[90m";
const BRIGHT_RED = "\x1b[91m";
const BRIGHT_GREEN = "\x1b[92m";
const BRIGHT_YELLOW = "\x1b[93m";
const BRIGHT_BLUE = "\x1b[94m";
const BRIGHT_MAGENTA = "\x1b[95m";
const BRIGHT_CYAN = "\x1b[96m";
const WHITE = "\x1b[97m";

const RESET = "\x1b[0m"; // called to return to standard terminal text color

// ---------------

const FORMAT = `${DARK_GRAY}{row} ${BRIGHT_GREEN}{server_name} ${LIGHT_GRAY}{timestamp_fmt} ${BRIGHT_MAGENTA}{username}${RESET}: {message}`;

const fileArg = process.argv[2];

const file = readFileSync(fileArg, "utf-8");
const [header, ...rest] = file.split("\n");

const data = rest.join("\n");
const headerFields = header
	.trim()
	.replaceAll('"', "")
	.replaceAll(" ", "_")
	.split(",")
	.map((value) => value.toLowerCase());
const pattern = headerFields
	.map((field) => `\\"(?<${field}>[^\\"]*?)\\"`)
	.join(",");

console.log(pattern);
const regExp = new RegExp(pattern, "gi");

const messages = [];

function formatDateIdentifier(identifier) {
	return String(identifier).padStart(2, "0");
}

function formatDate(date) {
	const prefix = [
		date.getUTCFullYear(),
		date.getUTCMonth() + 1,
		date.getUTCDate(),
	]
		.map((identifier) => formatDateIdentifier(identifier))
		.join("-");

	const time = [date.getUTCHours(), date.getUTCMinutes()]
		.map((identifier) => formatDateIdentifier(identifier))
		.join(":");

	return `${prefix} ${time}`;
}

let match;
let counter = 0;
while ((match = regExp.exec(data)) !== null) {
	const message = { ...match.groups, row: ++counter };

	const date = new Date(message.timestamp);
	const formattedTimestamp = formatDate(date);

	message["timestamp_fmt"] = formattedTimestamp;
	message["timestamp_num"] = date.getTime();

	messages.push(message);
}

messages.sort((first, second) => first.timestamp_num - second.timestamp_num);

for (const message of messages) {
	let out = FORMAT;

	out = out.replaceAll(/{(.+?)}/gi, (_pattern) => {
		const pattern = _pattern.replaceAll("{", "").replaceAll("}", "");
		return message[pattern] ?? "-";
	});

	console.log(out);
}
