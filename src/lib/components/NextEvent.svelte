<script>
	import { onMount } from 'svelte';
	import { base } from '$app/paths';
	import { splitEvents, eventTitle, eventWhere } from '$lib/events.js';
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
	const month = $derived(next?.when.toLocaleDateString('en-GB', { month: 'short' }));
	const monthLong = $derived(next?.when.toLocaleDateString('en-GB', { month: 'long' }));
	const weekday = $derived(next?.when.toLocaleDateString('en-GB', { weekday: 'long' }));
	const year = $derived(next?.when.getFullYear());

	/** "Tonight", "Tomorrow", "In 6 days" - the thing you actually want to know. */
	const countdown = $derived.by(() => {
		if (!next) return null;
		const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
		const days = Math.round((next.when - today) / 86400000);
		if (days <= 0) return 'Tonight';
		if (days === 1) return 'Tomorrow';
		if (days < 7) return `In ${days} days`;
		if (days < 14) return 'Next week';
		if (days < 60) return `In ${Math.round(days / 7)} weeks`;
		return null;
	});
</script>

{#if next}
	<aside class="next">
		<div class="next__bar">
			<h2 class="next__label">Next event</h2>
			{#if countdown}<span class="next__countdown">{countdown}</span>{/if}
		</div>

		<div class="next__head">
			<p class="next__date" aria-hidden="true">
				<span class="next__day">{day}</span>
				<span class="next__rest">{month}<br />{year}</span>
			</p>

			<div class="next__what">
				<h3 class="next__title">
					{#if next.url}
						<a href={next.url} target="_blank" rel="noopener noreferrer">{eventTitle(next)}</a>
					{:else}{eventTitle(next)}{/if}
				</h3>
				<p class="next__meta">
					<time datetime={next.date}>
						<span class="sr-only">{weekday} {day} {monthLong} {year}</span>
						<span aria-hidden="true">{weekday}</span>
					</time>
					<span aria-hidden="true">·</span>
					<span>{eventWhere(next)}</span>
				</p>
			</div>
		</div>

		<Lineup lineup={next.lineup} prominent />

		<div class="next__foot">
			{#if next.url}
				<a class="next__cta" href={next.url} target="_blank" rel="noopener noreferrer">Tickets</a>
			{/if}
			<AddToCalendar event={next} />
		</div>
	</aside>
{:else}
	<aside class="next next--empty">
		<div class="next__bar"><h2 class="next__label">Next event</h2></div>
		<p class="next__meta">
			Nothing announced yet — see <a href="{base}/upcoming-dates">upcoming dates</a>.
		</p>
	</aside>
{/if}

<style>
	/* Light card. The weight comes from the scale of the date and title and from
	   two solid dark elements - the countdown and the Tickets pill - rather than
	   from inverting the whole block. */
	.next {
		position: relative;
		margin: 2.5rem 0 3rem;
		padding: 1.6rem 1.75rem 1.5rem;
		border: 1px solid var(--rule);
		border-radius: 12px;
		background: var(--surface);
		overflow: hidden;
	}

	.next::before {
		content: '';
		position: absolute;
		inset: 0 0 auto;
		height: 4px;
		background: var(--ink);
	}

	.next__bar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		margin-bottom: 1.4rem;
	}

	.next__label {
		margin: 0;
		font-size: 0.72rem;
		font-weight: 700;
		letter-spacing: 0.22em;
		text-transform: uppercase;
		color: var(--text-muted);
	}

	.next__countdown {
		padding: 0.25rem 0.7rem;
		background: var(--ink);
		color: var(--paper);
		border-radius: 999px;
		font-size: 0.72rem;
		font-weight: 700;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		white-space: nowrap;
	}

	.next__head {
		display: flex;
		align-items: flex-start;
		gap: 1.2rem;
		padding-bottom: 1.3rem;
	}

	/* The day as the loudest thing on the page. */
	.next__date {
		display: flex;
		align-items: baseline;
		gap: 0.5rem;
		margin: 0;
		flex: 0 0 auto;
	}

	.next__day {
		font-size: 4.2rem;
		font-weight: 800;
		line-height: 0.82;
		letter-spacing: -0.05em;
		font-variant-numeric: tabular-nums;
	}

	.next__rest {
		font-size: 0.78rem;
		font-weight: 700;
		line-height: 1.25;
		letter-spacing: 0.14em;
		text-transform: uppercase;
		color: var(--text-muted);
	}

	.next__what {
		min-width: 0;
	}

	.next__title {
		margin: 0;
		font-size: 2rem;
		font-weight: 800;
		line-height: 1.05;
		letter-spacing: -0.025em;
	}

	.next__title a {
		color: inherit;
		text-decoration: none;
	}

	.next__title a:hover {
		text-decoration: underline;
	}

	/* The day and the venue are what someone actually needs off this card, so
	   they sit close to the title in weight rather than as fine print. */
	.next__meta {
		margin: 0.45rem 0 0;
		color: var(--text);
		font-size: 1.15rem;
		font-weight: 600;
		line-height: 1.3;
	}

	.next__meta [aria-hidden='true'] {
		color: var(--text-muted);
		font-weight: 400;
	}

	.next__meta span {
		margin-left: 0.25rem;
	}

	.sr-only {
		position: absolute;
		width: 1px;
		height: 1px;
		margin: -1px;
		padding: 0;
		overflow: hidden;
		clip-path: inset(50%);
		white-space: nowrap;
	}

	.next__meta time span.sr-only {
		margin-left: 0;
	}

	.next__foot {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.9rem;
		margin-top: 1.2rem;
	}

	.next__cta {
		padding: 0.5rem 1.2rem;
		border-radius: 999px;
		background: var(--ink);
		color: var(--paper);
		font-size: 0.9rem;
		font-weight: 700;
		text-decoration: none;
		white-space: nowrap;
	}

	.next__cta:hover {
		background: color-mix(in srgb, var(--ink) 80%, var(--paper));
	}

	/* The calendar row sits on the same line as Tickets and needs no top rule. */
	.next__foot :global(.cal) {
		margin-top: 0;
		padding-top: 0;
		border-top: 0;
	}

	.next--empty::before {
		background: var(--rule);
	}

	@media (max-width: 34rem) {
		.next {
			padding: 1.25rem 1.15rem 1.2rem;
		}

		.next__head {
			gap: 0.9rem;
		}

		.next__day {
			font-size: 3.2rem;
		}

		.next__title {
			font-size: 1.5rem;
		}

		.next__meta {
			font-size: 1.05rem;
		}
	}
</style>
