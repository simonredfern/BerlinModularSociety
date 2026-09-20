import { SITE_URL } from '$lib/site.js';

// Prerendered to a real file. Super served a sitemap and the migration dropped
// one; this rebuilds it from the content files, so a page added later is included
// without anyone remembering to update a list.
export const prerender = true;

const pages = import.meta.glob('/src/content/**/*.md', { eager: true });

export function GET() {
	const urls = Object.entries(pages)
		.map(([file, mod]) => ({
			path: file.replace('/src/content/', '').replace(/\.md$/, ''),
			meta: mod.metadata ?? {}
		}))
		// events/ are rendered inside /event-archive, not as pages of their own,
		// and a page that only redirects should not be advertised.
		.filter(({ path, meta }) => !path.startsWith('events/') && !meta.redirect)
		.map(({ path }) => (path === 'index' ? '' : path))
		.sort();

	const body = [
		'<?xml version="1.0" encoding="UTF-8"?>',
		'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
		...urls.map((p) => `\t<url><loc>${SITE_URL}/${p}</loc></url>`),
		'</urlset>',
		''
	].join('\n');

	return new Response(body, { headers: { 'content-type': 'application/xml' } });
}
