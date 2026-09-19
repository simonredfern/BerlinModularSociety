import { error } from '@sveltejs/kit';
import events from '$lib/data/events.json';
import { icsFor } from '$lib/calendar.js';

// Prerendered to a real file, so "add to calendar" is a plain link - no JS, and
// nothing runs on a server.
export const prerender = true;

export function entries() {
	return events.filter((e) => e.date).map((e) => ({ slug: e.slug }));
}

export function GET({ params }) {
	const e = events.find((x) => x.slug === params.slug && x.date);
	if (!e) error(404, 'No such event');

	// These headers only apply where something actually runs this handler - `npm
	// run dev` and `npm run preview`. adapter-static keeps the body and discards
	// the headers, so on GitHub Pages the file is served with whatever MIME type
	// Pages infers from the .ics extension. That is why the link in
	// AddToCalendar.svelte carries a `download` attribute: it pins the filename
	// and the save behaviour regardless of what the host sends back.
	return new Response(icsFor(e), {
		headers: {
			'content-type': 'text/calendar; charset=utf-8',
			'content-disposition': `attachment; filename="${e.slug}.ics"`
		}
	});
}
