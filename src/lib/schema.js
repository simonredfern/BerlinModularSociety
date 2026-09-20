import { SITE_URL, SITE_NAME } from '$lib/site.js';
import links from '$lib/data/links.json';
import { eventWindow } from '$lib/calendar.js';
import { eventTitle, splitEvents } from '$lib/events.js';

/**
 * schema.org JSON-LD.
 *
 * The site holds 59 dated, venued, line-upped events, which is exactly what
 * search engines want for event rich results - a listing that can show the date
 * and venue directly in the results rather than just a blue link.
 */

export function organisation() {
	return {
		'@context': 'https://schema.org',
		'@type': 'Organization',
		name: SITE_NAME,
		url: SITE_URL,
		logo: `${SITE_URL}/favicon.png`,
		email: links.email,
		description: 'We organise live modular music events in Berlin.',
		sameAs: [
			links.instagram,
			links.facebook,
			links.twitch,
			links.youtube,
			links.residentAdvisor
		].filter(Boolean)
	};
}

export function eventSchema(e) {
	const { start, end } = eventWindow(e);

	// An upcoming event has no anchor on /event-archive - that page lists past
	// events only - so pointing there would give search engines a dead fragment.
	const upcoming = splitEvents().upcoming.some((u) => u.number === e.number);
	const url = upcoming ? `${SITE_URL}/upcoming-dates` : `${SITE_URL}/event-archive#${e.slug}`;

	const performers = (e.lineup ?? [])
		// "Ends" and "Talk with Freedom Boxes" are slots, not performers.
		.filter((a) => a.artists?.length)
		.map((a) => ({ '@type': 'PerformingGroup', name: a.act }));

	const schema = {
		'@context': 'https://schema.org',
		'@type': 'MusicEvent',
		name: `${SITE_NAME}: ${eventTitle(e)}`,
		startDate: start.toISOString(),
		endDate: end.toISOString(),
		eventStatus: 'https://schema.org/EventScheduled',
		eventAttendanceMode: 'https://schema.org/OfflineEventAttendanceMode',
		url,
		organizer: { '@type': 'Organization', name: SITE_NAME, url: SITE_URL }
	};

	if (e.venue) {
		schema.location = {
			'@type': 'Place',
			name: e.venue,
			address: {
				'@type': 'PostalAddress',
				addressLocality: e.city ?? 'Berlin',
				addressCountry: e.city === 'Utrecht' ? 'NL' : 'DE'
			}
		};
	}
	if (performers.length) schema.performer = performers;
	if (e.image) schema.image = `${SITE_URL}/images/${e.image}-1280.jpg`;
	if (e.url) {
		schema.offers = {
			'@type': 'Offer',
			url: e.url,
			availability: 'https://schema.org/InStock'
		};
	}
	return schema;
}
