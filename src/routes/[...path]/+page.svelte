<script>
	import Seo from '$lib/components/Seo.svelte';
	import Breadcrumb from '$lib/components/Breadcrumb.svelte';
	import PageHeader from '$lib/components/PageHeader.svelte';

	let { data } = $props();

	const Content = $derived(data.content);
	const title = $derived(data.meta.title ?? data.path);
</script>

<Seo {title} description={data.meta.description} image={data.meta.cover} />

<Breadcrumb path={data.path} />

<PageHeader {title} cover={data.meta.cover} icon={data.meta.icon} />

<Content />
