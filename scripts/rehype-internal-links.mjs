import { visit } from 'unist-util-visit';

/**
 * Prefixes root-relative links written inside markdown with the configured base path.
 *
 * Components get this from `$app/paths`, but markdown is plain text, so `[x](/module-co2e)`
 * would point at the server root and 404 when the site is served from a subdirectory
 * (e.g. username.github.io/repo). Applied at build time from BASE_PATH.
 */
export default function rehypeInternalLinks() {
	const base = process.env.BASE_PATH ?? '';
	return (tree) => {
		if (!base) return;
		visit(tree, 'element', (node) => {
			if (node.tagName !== 'a') return;
			const href = node.properties?.href;
			// Root-relative only: skip external, anchors, and already-prefixed links.
			if (typeof href !== 'string' || !href.startsWith('/') || href.startsWith('//')) return;
			if (href.startsWith(base + '/') || href === base) return;
			node.properties.href = base + href;
		});
	};
}
