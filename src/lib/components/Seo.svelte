<script>
	import { base } from '$app/paths';
	import { page } from '$app/state';

	let { title, description = '', image = null } = $props();

	const SITE = 'Berlin Modular Society';
	// The homepage's own title is the site name; do not render it twice.
	const full = $derived(
		title && title !== 'Home' && title !== SITE
			? `${title} — ${SITE}`
			: `${SITE} — Live modular music events in Berlin`
	);

	// A page's cover photo makes a far better share card than the favicon.
	const ogImage = $derived(image ? `${base}/images/${image}-1280.jpg` : `${base}/favicon.png`);
	const canonical = $derived(new URL(page.url.pathname, 'https://berlinmodularsociety.com').href);
</script>

<svelte:head>
	<title>{full}</title>
	{#if description}<meta name="description" content={description} />{/if}
	<link rel="canonical" href={canonical} />

	<meta property="og:site_name" content={SITE} />
	<meta property="og:type" content="website" />
	<meta property="og:title" content={full} />
	<meta property="og:url" content={canonical} />
	{#if description}<meta property="og:description" content={description} />{/if}
	<meta property="og:image" content={new URL(ogImage, 'https://berlinmodularsociety.com').href} />

	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:title" content={full} />
	{#if description}<meta name="twitter:description" content={description} />{/if}
</svelte:head>
