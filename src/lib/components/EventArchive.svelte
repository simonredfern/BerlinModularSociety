<script>
	import { onMount } from 'svelte';
	import {
		splitEvents,
		formatEventDate,
		eventTitle,
		eventWhereLong,
		venueRenamedTo,
		noteParts
	} from '$lib/events.js';
	import Lineup from '$lib/components/Lineup.svelte';
	import Photo from '$lib/components/Photo.svelte';
	import JsonLd from '$lib/components/JsonLd.svelte';
	import { eventSchema } from '$lib/schema.js';

	let now = $state(new Date());
	const split = $derived(splitEvents(now));

	// Undated events are the earliest ones - the old site never recorded a date for
	// them. They belong in the archive, just at the end of it.
	const list = $derived([...split.past, ...split.undated]);
	const archive = $derived(list);

	// Each event's prose lives in src/content/events/<slug>.md so that mdsvex compiles
	// it and the <Photo> and <Embed> tags inside it are real components. Eager, because
	// the whole archive renders at once and every page here is prerendered anyway.
	const bodies = import.meta.glob('/src/content/events/*.md', { eager: true });

	function bodyOf(e) {
		return bodies[`/src/content/events/${e.slug}.md`]?.default;
	}

	onMount(() => {
		now = new Date();
	});
</script>

<JsonLd data={archive.filter((e) => e.date).map(eventSchema)} />

<div class="archive">
	{#each list as e (e.number)}
		{@const Body = bodyOf(e)}
		<article class="entry" id={e.slug}>
			<h2>
				{eventTitle(e)}
				<a class="heading-anchor" href="#{e.slug}" aria-hidden="true" tabindex="-1">#</a>
			</h2>

			<p class="entry__meta">
				{#if e.when}
					<time datetime={e.date}>{formatEventDate(e.when)}</time>
				{:else}
					<span class="entry__undated">date not recorded</span>
				{/if}
				{#if e.venue}
					<span>· {eventWhereLong(e)}</span>
					{#if venueRenamedTo(e.venue)}
						<span class="entry__renamed">(now {venueRenamedTo(e.venue)})</span>
					{/if}
				{/if}
				{#if e.url}
					<span>· <a href={e.url} target="_blank" rel="noopener noreferrer">tickets</a></span>
				{/if}
			</p>

			<!-- The event's own flyer or still. Events migrated from the old site
			     carry their images inside the body instead; this is for the ones
			     where the picture is all there was. -->
			{#if e.note}
			<p class="entry__note entry__note--plain">
				{#each noteParts(e.note) as part}{#if part.href}<a href={part.href} target="_blank" rel="noopener noreferrer">{part.text}</a>{:else}{part.text}{/if}{/each}
			</p>
		{/if}

			{#each e.images ?? [] as img (img)}
				<div class="entry__image">
					<Photo id={img} sizes="(max-width: 46rem) 100vw, 30rem" />
				</div>
			{/each}

			<Lineup lineup={e.lineup} />

			<!-- The archive is the master record. Where the Facebook event billed
			     something different, say so rather than quietly picking one. -->
			{#if e.facebookNote}
				<p class="entry__note">{e.facebookNote}</p>
			{/if}

			{#if Body}<Body />{/if}
		</article>
	{/each}
</div>

<style>
	.archive {
		margin: 2rem 0;
	}

	.entry {
		padding: 2rem 0;
		border-top: 1px solid var(--rule);
	}

	.entry :global(h2) {
		margin-top: 0;
	}

	.entry__meta {
		margin: -0.5rem 0 1rem;
		color: var(--text-muted);
		font-size: 0.95rem;
	}

	.entry__undated {
		font-style: italic;
	}

	.entry__renamed {
		opacity: 0.75;
	}

	.entry__note--plain {
		padding-left: 0;
		border-left: 0;
		color: var(--text);
		font-size: 1rem;
	}

	.entry__note {
		margin: 1rem 0;
		padding-left: 0.9rem;
		border-left: 2px solid var(--rule);
		color: var(--text-muted);
		font-size: 0.92rem;
	}

	/* A flyer is a poster, not a photograph - it does not need the full measure. */
	.entry__image {
		max-width: 30rem;
	}

	.entry__image :global(figure) {
		margin: 1.25rem 0;
	}
</style>
