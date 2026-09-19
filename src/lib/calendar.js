import { eventTitle, eventWhere } from '$lib/events.js';

const TZ = 'Europe/Berlin';

/** How far `tz` was from UTC at this instant, in milliseconds. */
function tzOffsetMs(utcMs, tz) {
	const parts = new Intl.DateTimeFormat('en-US', {
		timeZone: tz,
		hour12: false,
		year: 'numeric',
		month: '2-digit',
		day: '2-digit',
		hour: '2-digit',
		minute: '2-digit',
		second: '2-digit'
	})
		.formatToParts(new Date(utcMs))
		.reduce((a, p) => ((a[p.type] = p.value), a), {});

	const asIfUtc = Date.UTC(
		+parts.year,
		+parts.month - 1,
		+parts.day,
		+parts.hour % 24,
		+parts.minute,
		+parts.second
	);
	return asIfUtc - utcMs;
}

/**
 * A wall-clock time in Berlin, as a real instant.
 *
 * Two passes, because the offset depends on the instant we are still solving
 * for - one iteration settles it either side of a DST change.
 */
function berlinToUtc(y, m, d, hh, mm) {
	const wall = Date.UTC(y, m - 1, d, hh, mm);
	let guess = wall;
	for (let i = 0; i < 2; i++) guess = wall - tzOffsetMs(guess, TZ);
	return new Date(guess);
}

/**
 * When an event starts and ends, from its running order.
 *
 * Times run past midnight - a bill that ends at 04:00 ends the following
 * morning - so a time earlier than the one before it rolls the day over.
 */
export function eventWindow(e) {
	const [y, m, d] = e.date.split('-').map(Number);

	// Some line-ups are just a list of names - the early events were announced on
	// a flyer with no set times. Those get the same placeholder as no line-up at all.
	const timed = (e.lineup ?? []).filter((a) => a.time);

	if (!timed.length) {
		// No running order: an all-evening placeholder rather than a false precision.
		return { start: berlinToUtc(y, m, d, 20, 0), end: berlinToUtc(y, m, d + 1, 2, 0) };
	}

	let dayOffset = 0;
	let prev = -1;
	const stamps = timed.map((a) => {
		const [hh, mm] = a.time.split(':').map(Number);
		const mins = hh * 60 + mm;
		if (mins < prev) dayOffset += 1;
		prev = mins;
		return berlinToUtc(y, m, d + dayOffset, hh, mm);
	});

	const start = stamps[0];
	let end = stamps[stamps.length - 1];
	// A single-act bill, or one whose last entry is the first act, still needs
	// some duration on it.
	if (end <= start) end = new Date(start.getTime() + 3 * 3600 * 1000);
	return { start, end };
}

/** The running order as text, with times only where the event had them. */
function lineupText(e) {
	if (!e.lineup?.length) return null;
	return e.lineup.map((a) => (a.time ? `${a.time}  ${a.act}` : a.act)).join('\n');
}

const stampUtc = (d) => d.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}/, '');

export function googleCalendarUrl(e) {
	const { start, end } = eventWindow(e);
	const details = [
		lineupText(e),
		e.url ? `Tickets: ${e.url}` : null,
		'https://berlinmodularsociety.com/upcoming-dates'
	]
		.filter(Boolean)
		.join('\n\n');

	const q = new URLSearchParams({
		action: 'TEMPLATE',
		text: `Berlin Modular Society: ${eventTitle(e)}`,
		dates: `${stampUtc(start)}/${stampUtc(end)}`,
		location: eventWhere(e),
		details,
		ctz: TZ
	});
	return `https://calendar.google.com/calendar/render?${q}`;
}

/**
 * RFC 5545 wants CRLF, escaped separators, and lines folded at 75 *octets*.
 *
 * Octets, not characters - an em-dash is three bytes, so counting characters
 * would let a line through that is over the limit, and could split a multi-byte
 * character down the middle.
 */
const enc = new TextEncoder();

function fold(line) {
	const out = [];
	let cur = '';
	let bytes = 0;
	for (const ch of line) {
		const n = enc.encode(ch).length;
		// 74 on the first line, 73 after, leaving room for the leading space.
		const limit = out.length === 0 ? 75 : 74;
		if (bytes + n > limit) {
			out.push(cur);
			cur = ch;
			bytes = n;
		} else {
			cur += ch;
			bytes += n;
		}
	}
	out.push(cur);
	return out.map((l, i) => (i === 0 ? l : ' ' + l)).join('\r\n');
}

const esc = (s) =>
	String(s ?? '')
		.replace(/\\/g, '\\\\')
		.replace(/;/g, '\;')
		.replace(/,/g, '\\,')
		.replace(/\n/g, '\\n');

export function icsFor(e) {
	const { start, end } = eventWindow(e);
	const description = [
		lineupText(e),
		e.url ? `Tickets: ${e.url}` : null
	]
		.filter(Boolean)
		.join('\n\n');

	return [
		'BEGIN:VCALENDAR',
		'VERSION:2.0',
		'PRODID:-//Berlin Modular Society//berlinmodularsociety.com//EN',
		'CALSCALE:GREGORIAN',
		'METHOD:PUBLISH',
		'BEGIN:VEVENT',
		`UID:${e.slug}@berlinmodularsociety.com`,
		// Fixed, not "now": a rebuild should not produce a different file and make
		// every subscriber's client think the event changed.
		`DTSTAMP:${stampUtc(start)}`,
		`DTSTART:${stampUtc(start)}`,
		`DTEND:${stampUtc(end)}`,
		fold(`SUMMARY:${esc(`Berlin Modular Society: ${eventTitle(e)}`)}`),
		fold(`LOCATION:${esc(eventWhere(e))}`),
		fold(`DESCRIPTION:${esc(description)}`),
		fold(`URL:${esc(e.url || 'https://berlinmodularsociety.com/upcoming-dates')}`),
		'END:VEVENT',
		'END:VCALENDAR',
		''
	].join('\r\n');
}
