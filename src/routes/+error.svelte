<script>
	import { base } from '$app/paths';
	import { page } from '$app/state';
	import nav from '$lib/data/nav.json';
</script>

<svelte:head><title>{page.status} — Berlin Modular Society</title></svelte:head>

<h1>{page.status === 404 ? 'No such page' : 'Something went wrong'}</h1>

<p>{page.error?.message ?? 'Unknown error'}</p>

<p>Try one of these instead:</p>

<ul>
	{#each nav as item (item.slug)}
		<li><a href="{base}/{item.slug}">{item.title}</a></li>
	{/each}
</ul>
