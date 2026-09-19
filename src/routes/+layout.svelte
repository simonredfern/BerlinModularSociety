<script>
	import '../app.css';
	import Nav from '$lib/components/Nav.svelte';
	import Footer from '$lib/components/Footer.svelte';

	let { children } = $props();
</script>

<a class="skip" href="#main">Skip to content</a>

<Nav />

<main id="main" class="prose">
	{@render children?.()}
</main>

<Footer />

<style>
	.skip {
		position: absolute;
		left: -9999px;
		top: 0;
		z-index: 100;
		padding: 0.6rem 1rem;
		background: var(--bg);
	}

	.skip:focus {
		left: 0;
	}

	.prose {
		max-width: var(--measure);
		margin: 0 auto;
		padding: 2.5rem 1rem 1rem;
	}

	/* Markdown content is injected here, so these need :global. */
	.prose :global(ul),
	.prose :global(ol) {
		padding-left: 1.3rem;
	}

	.prose :global(li) {
		margin-bottom: 0.35rem;
	}

	.prose :global(blockquote) {
		margin: 1.5rem 0;
		padding-left: 1.1rem;
		border-left: 3px solid var(--rule);
		color: var(--text-muted);
	}

	.prose :global(code) {
		padding: 0.1em 0.35em;
		border-radius: 3px;
		background: var(--surface);
		font-family: var(--font-mono);
		font-size: 0.9em;
	}
</style>
