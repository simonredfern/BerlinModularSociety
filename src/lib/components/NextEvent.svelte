<script>
	import { onMount } from 'svelte';
	import { base } from '$app/paths';
	import { splitEvents, eventTitle, eventWhereLong } from '$lib/events.js';
	import Lineup from '$lib/components/Lineup.svelte';
	import AddToCalendar from '$lib/components/AddToCalendar.svelte';

	let now = $state(new Date());
	const split = $derived(splitEvents(now));
	const next = $derived(split.upcoming[0]);

	// The prerendered HTML is stamped with the build date; correct it in the browser.
	onMount(() => {
		now = new Date();
	});

	const day = $derived(next?.when.toLocaleDateString('en-GB', { day: 'numeric' }));
	const monthLong = $derived(next?.when.toLocaleDateString('en-GB', { month: 'long' }));
	const weekday = $derived(next?.when.toLocaleDateString('en-GB', { weekday: 'long' }));
	const year = $derived(next?.when.getFullYear());

	/** Completes the sentence "Next event is …". Null when it is far enough off
	    that a countdown says nothing useful. */
	const countdown = $derived.by(() => {
		if (!next) return null;
		const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
		const days = Math.round((next.when - today) / 86400000);
		if (days <= 0) return 'tonight';
		if (days === 1) return 'tomorrow';
		if (days < 7) return `in ${days} days`;
		if (days < 14) return 'next week';
		if (days < 60) return `in ${Math.round(days / 7)} weeks`;
		return null;
	});
</script>

{#if next}
	<aside class="next">
		<h2 class="next__label">Next event{#if countdown} is {countdown}{/if}</h2>

		<h3 class="next__title">
			{#if next.url}
				<a href={next.url} target="_blank" rel="noopener noreferrer">{eventTitle(next)}</a>
			{:else}{eventTitle(next)}{/if}
		</h3>

		<p class="next__meta">
			<time datetime={next.date}>{weekday} {day} {monthLong} {year}</time>
			at {eventWhereLong(next)}
		</p>

		<Lineup lineup={next.lineup} />

		<div class="next__foot">
			{#if next.url}
				<a class="next__cta" href={next.url} target="_blank" rel="noopener noreferrer">Tickets</a>
			{/if}
			<AddToCalendar event={next} />
		</div>
	</aside>
{:else}
	<aside class="next next--empty">
		<h2 class="next__label">Next event</h2>
		<p class="next__meta">
			Nothing announced yet — see <a href="{base}/upcoming-dates">upcoming dates</a>.
		</p>
	</aside>
{/if}

<style>
	/*
	 * Deliberately plain. The headings, body text and links are the page's own,
	 * so this reads as part of the site rather than as a widget dropped into it.
	 * The only styled things are the countdown and the two buttons.
	 */
	.next {
		margin: 2.5rem 0 3rem;
	}

	/* Plain sentence case at body size - no caps, no letterspacing. It is a
	   label, not a banner. */
	.next__label {
		margin: 0;
		font-size: 1rem;
		font-weight: 600;
		color: var(--text-muted);
	}

	/* The title and the date/venue are the call to action, so they outrank the
	   "Next event" label above them. */
	.next__title {
		margin: 0.5rem 0 0;
		font-size: clamp(1.7rem, 4.5vw, 2.3rem);
		font-weight: 700;
		line-height: 1.1;
		letter-spacing: -0.02em;
	}

	.next__title a {
		color: inherit;
		text-decoration: none;
	}

	.next__title a:hover {
		text-decoration: underline;
	}

	.next__meta {
		margin: 0.35rem 0 0;
		font-size: 1.2rem;
		font-weight: 600;
		line-height: 1.35;
	}

	.next__foot {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.75rem;
		margin-top: 1.2rem;
	}

	.next__cta {
		padding: 0.35rem 0.9rem;
		border: 1px solid var(--rule);
		border-radius: 3px;
		color: var(--text);
		font-size: 0.9rem;
		font-weight: 600;
		text-decoration: none;
		white-space: nowrap;
	}

	.next__cta:hover {
		border-color: var(--text);
	}

	/* Sits on the same row as Tickets, so it needs no rule above it. */
	.next__foot :global(.cal) {
		margin-top: 0;
		padding-top: 0;
		border-top: 0;
	}
</style>
