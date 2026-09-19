/**
 * Drop the "#" anchor from a heading that opens a page.
 *
 * rehype-autolink-headings gives every heading a link to itself, which is what
 * you want for a section someone might link to directly. A heading sitting at
 * the very top of the content is not that - it is the page, and the page
 * already has a URL. The anchor there is just a stray "#" after the first words
 * a visitor reads.
 *
 * Must run after rehype-autolink-headings, since it removes what that adds.
 */
const HEADINGS = new Set(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']);

const isAnchor = (node) => {
	const cn = node?.properties?.className;
	const list = Array.isArray(cn) ? cn : cn ? [cn] : [];
	return node?.tagName === 'a' && list.includes('heading-anchor');
};

export default function rehypeNoTopAnchor() {
	return (tree) => {
		// The first thing on the page, ignoring the whitespace between nodes.
		const first = tree.children.find(
			(n) => n.type === 'element' || (n.type === 'text' && n.value.trim())
		);
		if (!first || first.type !== 'element' || !HEADINGS.has(first.tagName)) return;

		first.children = first.children.filter((c) => !isAnchor(c));
	};
}
