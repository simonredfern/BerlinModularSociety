import events from '$lib/data/events.json';

/**
 * Every BMS event, past and upcoming, from the single list in events.json.
 *
 * Events are split relative to `now`. At build time that is the build date, so the
 * browser re-checks after hydration - otherwise an event would stay "upcoming" until
 * the next deploy. Schedule a periodic rebuild if you want the HTML itself fresh.
 */
export function splitEvents(now = new Date()) {
	const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

	const dated = events
		.filter((e) => e.date)
		.map((e) => ({ ...e, when: new Date(`${e.date}T00:00:00`) }))
		.filter((e) => !Number.isNaN(e.when.valueOf()));

	// The earliest BMS events were listed on the old site with no date at all. They
	// are real events, so they stay in the archive rather than being dropped.
	const undated = events.filter((e) => !e.date);

	return {
		upcoming: dated.filter((e) => e.when >= today).sort((a, b) => a.when - b.when),
		past: dated.filter((e) => e.when < today).sort((a, b) => b.when - a.when),
		undated
	};
}

export function formatEventDate(d) {
	return d.toLocaleDateString('en-GB', {
		weekday: 'long',
		day: 'numeric',
		month: 'long',
		year: 'numeric'
	});
}

/** "BMS59 — Pollen" or just "BMS59" when the event had no name of its own. */
export function eventTitle(e) {
	return e.name ? `${e.number} — ${e.name}` : e.number;
}

/**
 * Venues that have since been renamed.
 *
 * Events keep the name the place had on the night - that is what the posters and
 * the archive said. But three events at Holzmarktstrasse 15 are filed under Marie
 * Antoinette and a fourth under LARK, and nothing tells a reader they are the same
 * room. The archive notes the current name alongside the historic one.
 *
 * (Facebook shows only the current name for all of them, which is why its listing
 * is not used for venue names - see scripts/migration/events.py.)
 */
const RENAMED = {
	'Marie Antoinette': 'LARK'
};

/** The venue's name today, if it has changed since. */
export function venueRenamedTo(venue) {
	return RENAMED[venue] ?? null;
}

/**
 * The venue written out for a reader: "90Mil, near Jannowitzbrücke".
 *
 * `locality` holds the whole phrase, preposition included, because a station is
 * "near" and a district is "in" - and only the data knows which it is. More use
 * to someone deciding whether to come than the city, which is Berlin for all but
 * one event.
 */
export function eventWhereLong(e) {
	if (!e.venue) return e.city ?? '';
	if (e.locality) return `${e.venue}, ${e.locality}`;
	return eventWhere(e);
}

export function eventWhere(e) {
	return [e.venue, e.venue === e.city ? null : e.city].filter(Boolean).join(', ');
}
