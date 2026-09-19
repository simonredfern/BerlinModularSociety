import adapter from '@sveltejs/adapter-static';
import { mdsvex } from 'mdsvex';
import rehypeSlug from 'rehype-slug';
import rehypeAutolinkHeadings from 'rehype-autolink-headings';
import rehypeNoTopAnchor from './scripts/rehype-no-top-anchor.mjs';
import rehypeExternalLinks from './scripts/rehype-external-links.mjs';
import rehypeInternalLinks from './scripts/rehype-internal-links.mjs';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	extensions: ['.svelte', '.md'],

	preprocess: [
		mdsvex({
			extensions: ['.md'],
			rehypePlugins: [
				// Readable, stable heading ids - the thing Notion/Super would not give us.
				rehypeSlug,
				[
					rehypeAutolinkHeadings,
					{
						behavior: 'append',
						properties: { className: 'heading-anchor', ariaHidden: 'true', tabIndex: -1 },
						content: { type: 'text', value: '#' }
					}
				],
				// After the autolink plugin: it removes what that one adds.
				rehypeNoTopAnchor,
				rehypeExternalLinks,
				rehypeInternalLinks
			]
		})
	],

	kit: {
		// Empty for a custom domain (berlinmodularsociety.com). Set BASE_PATH=/repo-name
		// to serve from a GitHub Pages project URL, e.g. username.github.io/repo-name.
		paths: { base: process.env.BASE_PATH ?? '' },

		// Plain files on a CDN. Nothing runs on a server in production.
		// fallback: GitHub Pages serves 404.html for any unmatched path, and that page
		// boots the app client-side so +error.svelte renders instead of GitHub's own 404.
		adapter: adapter({ fallback: '404.html', strict: true }),
		prerender: { handleHttpError: 'fail' }
	}
};

export default config;
