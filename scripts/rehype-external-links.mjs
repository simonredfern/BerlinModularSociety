import { visit } from 'unist-util-visit';

/**
 * mdsvex stamps rel="nofollow" on every external link by default. This site links to
 * venues, collaborators and artists on purpose, so we do not want to withhold credit
 * from them. Open externals in a new tab, keep the security rels, drop nofollow.
 */
export default function rehypeExternalLinks() {
	return (tree) => {
		visit(tree, 'element', (node) => {
			if (node.tagName !== 'a') return;
			const href = node.properties?.href;
			if (typeof href !== 'string' || !/^https?:\/\//i.test(href)) return;

			node.properties.target = '_blank';
			node.properties.rel = ['noopener', 'noreferrer'];
		});
	};
}
