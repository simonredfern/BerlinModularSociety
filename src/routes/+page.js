import { error } from '@sveltejs/kit';

// Loaded through a glob rather than a static `import ... from '$content/index.md'`.
// Vite's dependency pre-scanner runs esbuild before mdsvex has processed the file, so a
// static import makes `vite dev` fail with: No matching export ... for import "metadata".
const modules = import.meta.glob('/src/content/*.md');

export async function load() {
	const loader = modules['/src/content/index.md'];
	if (!loader) error(500, 'src/content/index.md is missing');

	const mod = await loader();
	return { content: mod.default, meta: mod.metadata ?? {} };
}
