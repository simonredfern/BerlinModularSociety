import { error } from '@sveltejs/kit';
import pages from '$lib/data/pages.json';

const modules = import.meta.glob('/src/content/**/*.md');

/**
 * Every page, including nested ones, so the prerenderer emits a file for each.
 *
 * Derived from the content files rather than from pages.json: pages.json is
 * written by the migration script and would not know about a page added by hand
 * afterwards, which would then 404 in production while working fine in dev.
 * src/content/events/ is excluded - those are rendered inside /event-archive,
 * not as pages of their own.
 */
export function entries() {
	return Object.keys(modules)
		.map((f) => f.replace('/src/content/', '').replace(/\.md$/, ''))
		.filter((path) => path !== 'index' && !path.startsWith('events/'))
		.map((path) => ({ path }));
}

export async function load({ params }) {
	// index.md is served at "/" - do not also expose it at "/index".
	if (params.path === 'index') error(404, 'Not found');

	const loader = modules[`/src/content/${params.path}.md`];
	if (!loader) error(404, `No page at /${params.path}`);

	const mod = await loader();
	return {
		path: params.path,
		content: mod.default,
		meta: mod.metadata ?? {}
	};
}
