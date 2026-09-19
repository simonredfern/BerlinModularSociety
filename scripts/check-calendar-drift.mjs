/**
 * Compare the public Google Calendar against src/lib/data/events.json.
 *
 * Sources of truth, in order:
 *
 *   1. Facebook  - for BMS1-BMS9 and BMSAV1, which predate the old site. Those
 *                  dates are copied into POST_FIXES in scripts/migration/events.py.
 *   2. The event archive - everything else. It is now src/lib/data/events.json.
 *
 * The Google Calendar is NOT a source of truth. It is a publishing target: people
 * subscribed to it years ago, so it has to be kept current, but where it disagrees
 * with events.json it is the calendar that is wrong. It went unmaintained for most
 * of 2025, which is how it came to be missing BMS56 and BMS59 entirely.
 *
 * So this check asks one question - is the calendar up to date? - and not "which
 * of these two is right".
 *
 * Read-only, and the calendar is public, so this needs no credentials and cannot
 * damage anyone's subscription.
 *
 *   node scripts/check-calendar-drift.mjs            report, always exit 0
 *   node scripts/check-calendar-drift.mjs --strict   exit 1 if anything drifted
 */
import { readFileSync } from 'node:fs';

const STRICT = process.argv.includes('--strict');
const TZ = 'Europe/Berlin';


const links = JSON.parse(readFileSync('src/lib/data/links.json', 'utf8'));
const events = JSON.parse(readFileSync('src/lib/data/events.json', 'utf8'));

const calendarId = links.googleCalendarId;
if (!calendarId) {
	console.error('No googleCalendarId in src/lib/data/links.json');
	process.exit(2);
}

/* The embed on /upcoming-dates carries the same id, base64-encoded in its `src`.
   If the two ever diverge this check would be watching a calendar nobody sees. */
function checkEmbedMatches() {
	const md = readFileSync('src/content/upcoming-dates.md', 'utf8');
	const m = md.match(/calendar\.google\.com\/calendar\/embed[^"]*?[?&]src=([A-Za-z0-9_-]+)/);
	if (!m) return 'no Google Calendar embed found on /upcoming-dates';
	const embedded = Buffer.from(m[1], 'base64').toString('utf8');
	if (embedded !== calendarId) {
		return `the embed on /upcoming-dates points at ${embedded}, not ${calendarId}`;
	}
	return null;
}

/** Unfold continuation lines, then pull out the VEVENTs. */
function parseIcs(text) {
	const lines = [];
	for (const raw of text.split(/\r?\n/)) {
		if (/^[ \t]/.test(raw) && lines.length) lines[lines.length - 1] += raw.slice(1);
		else lines.push(raw);
	}

	const out = [];
	let cur = null;
	for (const line of lines) {
		if (line === 'BEGIN:VEVENT') cur = {};
		else if (line === 'END:VEVENT') {
			if (cur) out.push(cur);
			cur = null;
		} else if (cur) {
			const i = line.indexOf(':');
			if (i < 0) continue;
			const [name, ...params] = line.slice(0, i).split(';');
			cur[name] = { value: line.slice(i + 1), params };
		}
	}
	return out;
}

const dateParts = new Intl.DateTimeFormat('en-CA', {
	timeZone: TZ,
	year: 'numeric',
	month: '2-digit',
	day: '2-digit'
});

/** The local Berlin date an event falls on, whatever form its DTSTART took. */
function localDate(prop) {
	const v = prop.value;
	const ymd = `${v.slice(0, 4)}-${v.slice(4, 6)}-${v.slice(6, 8)}`;
	if (prop.params.includes('VALUE=DATE') || !v.includes('T')) return ymd;
	if (!v.endsWith('Z')) return ymd; // TZID form - already local
	const utc = Date.UTC(
		+v.slice(0, 4),
		+v.slice(4, 6) - 1,
		+v.slice(6, 8),
		+v.slice(9, 11),
		+v.slice(11, 13),
		+v.slice(13, 15)
	);
	return dateParts.format(new Date(utc));
}

const unescapeIcs = (s) => s.replace(/\\n/g, ' ').replace(/\\([;,\\])/g, '$1');

const url = `https://calendar.google.com/calendar/ical/${encodeURIComponent(calendarId)}/public/basic.ics`;

const res = await fetch(url);
if (!res.ok) {
	console.error(`Could not read the calendar: ${res.status} ${res.statusText}`);
	console.error(url);
	process.exit(2);
}

const google = new Map();
const unmatched = [];
for (const ev of parseIcs(await res.text())) {
	if (!ev.DTSTART) continue;
	const summary = unescapeIcs(ev.SUMMARY?.value ?? '');
	const date = localDate(ev.DTSTART);
	const m = summary.match(/\bBMS\s*#?(\d+)\b/i);
	if (m) google.set(`BMS${m[1]}`, { date, summary });
	else unmatched.push({ date, summary });
}

const today = new Date().toISOString().slice(0, 10);
const dated = events.filter((e) => e.date);
const upcoming = dated.filter((e) => e.date >= today);

const problems = [];

/* Only upcoming events have to be in Google. The calendar starts in late 2022,
   so demanding the whole archive would report the same two dozen gaps forever. */
for (const e of upcoming) {
	if (!google.has(e.number)) {
		problems.push({
			kind: 'missing',
			text: `${e.number} (${e.date}, ${e.venue ?? 'venue tbc'}) is not in the Google calendar`
		});
	}
}

/* A conflict on an UPCOMING event is urgent: a subscriber turns up on the wrong
   night. A conflict on a past one just means the calendar's history was never
   tidied - worth printing, not worth failing over or going back to fix. */
const staleHistory = [];
for (const e of dated) {
	const g = google.get(e.number);
	if (!g || g.date === e.date) continue;
	const text = `${e.number}: archive says ${e.date} (${e.venue ?? '-'}), Google says ${g.date} ("${g.summary}")`;
	if (e.date >= today) problems.push({ kind: 'conflict', text });
	else staleHistory.push(text);
}

const embedProblem = checkEmbedMatches();
if (embedProblem) problems.push({ kind: 'embed', text: embedProblem });

console.log(`Google calendar: ${google.size} BMS events, ${unmatched.length} unrecognised`);
console.log(`events.json:     ${dated.length} dated, ${upcoming.length} upcoming\n`);

if (!problems.length) {
	console.log('In step - every upcoming event is in the Google calendar, no date conflicts.');
} else {
	for (const kind of ['missing', 'conflict', 'embed']) {
		const group = problems.filter((p) => p.kind === kind);
		if (!group.length) continue;
		const heading = {
			missing: 'Upcoming events missing from the Google calendar',
			conflict: 'Upcoming events on the wrong date in the Google calendar',
			embed: 'Embed mismatch'
		}[kind];
		console.log(`${heading}:`);
		for (const p of group) console.log(`  - ${p.text}`);
		console.log();
	}
	console.log('Fix these in Google Calendar. events.json is the source of truth;');
	console.log('only correct it if the archive itself turns out to be wrong.');
}

if (staleHistory.length) {
	console.log("\nPast events the calendar never caught up with (not failing - its");
	console.log('history is not worth backfilling):');
	for (const t of staleHistory) console.log(`  - ${t}`);
}

if (unmatched.length) {
	console.log(`\nGoogle entries with no BMS number in the title (not checked):`);
	for (const u of unmatched.sort((a, b) => a.date.localeCompare(b.date))) {
		console.log(`  ${u.date}  ${u.summary}`);
	}
}

if (STRICT && problems.length) process.exit(1);
