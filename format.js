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

const FORMAT = `${DARK_GRAY}{row} [{platform_short}] ${BRIGHT_GREEN}{server_name} ${LIGHT_GRAY}{timestamp_fmt} ${BRIGHT_MAGENTA}{username}${RESET}: {message}`;

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
	message["platform_short"] = message.platform?.at(0).toUpperCase();

	messages.push(message);
}

messages.sort((first, second) => first.timestamp_num - second.timestamp_num);

const invites = new Set();

// https://gist.github.com/MBrassey/623f7b8d02766fa2d826bf9eca3fe005
const patterns = {
	BTC: /(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}/g,
	ETH: /0x[a-fA-F0-9]{40}/g, // ETH etc. ERC-20
	DASH: /X[1–9A-HJ-NP-Za-km-z]{33}/g,
	XMR: /[48][0–9AB][1–9A-HJ-NP-Za-km-z]{93}/g,
	ADA: /addr1[a-z0–9]/g,
	ATOM: /cosmos[a-zA-Z0–9_.-]{10,}/g,
	DOGE: /\sD[a-zA-Z0–9_.-]{33}/g,
	LTC: /[LM3][a-km-zA-HJ-NP-Z1–9]{26,33}/g,
	NEM: /[N][A-Za-z0–9-]{37,52}/g,
	NEO: /N[0–9a-zA-Z]{33}/g,
	ONT: /A[0–9a-zA-Z]{33}/g,
	DOT: /1[0–9a-zA-Z]{47}/g,
	XRP: /r[0–9a-zA-Z]{33}/g,
	XLM: /G[0–9A-Z]{40,60}/g,
};

function findWallets(text) {
	const matches = new Map();

	for (const [walletType, pattern] of Object.entries(patterns)) {
		let match;
		while ((match = pattern.exec(text)) !== null) {
			matches.set(match[0], walletType);
		}
	}

	return matches;
}

const wallets = new Map();
for (const message of messages) {
	let out = FORMAT;

	let match;
	const pattern = /t\.me\/(\S*)|\.gg\/(\S*)/gi;
	while ((match = pattern.exec(message?.message ?? "")) !== null) {
		invites.add(match[0]);
	}

	const foundWallets = findWallets(message.message ?? "");
	for (const [address, walletType] of foundWallets.entries()) {
		wallets.set(address, walletType);
	}

	out = out.replaceAll(/{(.+?)}/gi, (_pattern) => {
		const pattern = _pattern.replaceAll("{", "").replaceAll("}", "");
		if (pattern === "row") {
			return String(message["row"]).padStart(
				String(messages.length).length,
				" ",
			);
		}

		return message[pattern] ?? "-";
	});

	console.log(out);
}

console.log();
console.log(invites.size ? "# Found invites:" : "# Found no invites");
console.log([...invites].map((invite) => `- ${invite}`).join("\n"));
console.log();
console.log(
	wallets.size
		? "# Found potential wallet addresses:"
		: "# Found no potential wallet addresses",
);

for (const [address, walletType] of wallets) {
	console.log(`- [${walletType}] ${address}`);
}
