<script>
	/**
	 * Emits a schema.org block. The JSON is serialised here rather than in the
	 * template so that `<` inside any string cannot close the script tag early.
	 */
	let { data } = $props();

	const json = $derived(
		JSON.stringify(Array.isArray(data) && data.length === 1 ? data[0] : data).replace(
			/</g,
			'\\u003c'
		)
	);
</script>

<svelte:head>
	{@html `<script type="application/ld+json">${json}</` + `script>`}
</svelte:head>
