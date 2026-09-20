import { visit } from 'unist-util-visit';

/**
 * Rewrites root-relative markdown links to be relative to the page they sit on.
 *
 *   src/content/about.md                 /artist-area -> ./artist-area
 *   src/content/artist-area/using-obs.md /artist-area -> ../artist-area
 *
 * Why not just prefix the base path: SvelteKit already emits every link and asset
 * it controls as a relative URL, which is what lets the site work unchanged at
 * simonredfern.github.io/BerlinModularSociety and at berlinmodularsociety.com.
 * Markdown is plain text, so `[x](/artist-area)` escaped that and pointed at the
 * server root - fine at the apex, a 404 at the project URL.
 *
 * The previous version prefixed BASE_PATH instead. That only worked when the
 * variable was set, and in CI `actions/configure-pages` returns an empty
 * base_path, so the links shipped absolute and broke. Relative needs no
 * configuration and cannot drift out of step with where the site is served.
 */
export default function rehypeInternalLinks() {
	return (tree, file) => {
		const source = file?.filename ?? file?.path ?? file?.history?.[0] ?? '';
		const m = String(source).replace(/\\/g, '/').match(/src\/content\/(.+)\.md$/);
		// Unknown source: leave the link alone rather than guess at the depth.
		if (!m) return;

		// "artist-area/using-obs" sits one directory deep; "about" sits at the root.
		const depth = m[1] === 'index' ? 0 : m[1].split('/').length - 1;
		const prefix = depth === 0 ? './' : '../'.repeat(depth);

		visit(tree, 'element', (node) => {
			if (node.tagName !== 'a') return;
			const href = node.properties?.href;
			// Root-relative only: skip external, protocol-relative, anchors and mailto.
			if (typeof href !== 'string' || !href.startsWith('/') || href.startsWith('//')) return;
			node.properties.href = prefix + href.slice(1);
		});
	};
}
