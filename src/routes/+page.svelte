<script>
	import Seo from '$lib/components/Seo.svelte';
	import PageHeader from '$lib/components/PageHeader.svelte';

	let { data } = $props();

	const Content = $derived(data.content);
</script>

<Seo title={data.meta.title} description={data.meta.description} image={data.meta.cover} />

<PageHeader title={data.meta.title} cover={data.meta.cover} icon={data.meta.icon} />

<Content />
