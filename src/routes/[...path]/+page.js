import { error } from '@sveltejs/kit';
import pages from '$lib/data/pages.json';

const modules = import.meta.glob('/src/content/**/*.md');

/** Every page, including nested ones, so the prerenderer emits a file for each. */
export function entries() {
	return pages.filter((p) => p.path !== '').map((p) => ({ path: p.path }));
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
