<script>
	import Seo from '$lib/components/Seo.svelte';
	import PageHeader from '$lib/components/PageHeader.svelte';
	import JsonLd from '$lib/components/JsonLd.svelte';
	import { eventSchema } from '$lib/schema.js';
	import { splitEvents } from '$lib/events.js';

	let { data } = $props();

	const Content = $derived(data.content);
	const upcoming = splitEvents().upcoming.map(eventSchema);
</script>

<Seo title={data.meta.title} description={data.meta.description} image={data.meta.cover} />

{#if upcoming.length}<JsonLd data={upcoming} />{/if}

<PageHeader title={data.meta.title} cover={data.meta.cover} icon={data.meta.icon} />

<Content />
