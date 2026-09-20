<script>
	import { onMount } from 'svelte';
	import { base } from '$app/paths';
	import { goto } from '$app/navigation';
	import Seo from '$lib/components/Seo.svelte';
	import Breadcrumb from '$lib/components/Breadcrumb.svelte';
	import PageHeader from '$lib/components/PageHeader.svelte';

	let { data } = $props();

	const Content = $derived(data.content);
	const title = $derived(data.meta.title ?? data.path);

	/**
	 * A page can retire itself by putting `redirect: "/somewhere"` in its
	 * frontmatter. Nothing runs on a server here, so the redirect is a meta
	 * refresh - which works with JavaScript off - plus a client-side goto that
	 * beats the refresh when JavaScript is on, and a plain link if both fail.
	 */
	const redirect = $derived(data.meta.redirect ?? null);
	const target = $derived(redirect ? `${base}${redirect}` : null);

	onMount(() => {
		if (target) goto(target, { replaceState: true });
	});
</script>

<!-- svelte:head has to sit at the top level, so the condition goes inside it. -->
<svelte:head>
	{#if redirect}
		<meta http-equiv="refresh" content="0; url={target}" />
		<meta name="robots" content="noindex" />
		<link rel="canonical" href={target} />
	{/if}
</svelte:head>

{#if redirect}
	<h1>{title}</h1>
	<Content />
{:else}
	<Seo {title} description={data.meta.description} image={data.meta.cover} />

	<Breadcrumb path={data.path} />

	<PageHeader {title} cover={data.meta.cover} icon={data.meta.icon} />

	<Content />
{/if}
