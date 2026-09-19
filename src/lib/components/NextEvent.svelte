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
			<div class="next__date" aria-hidden="true">
				<span class="next__day">{day}</span>
				<span class="next__month">{month}</span>
			</div>

			<div class="next__what">
				<p class="next__title">
					{#if next.url}
						<a href={next.url} target="_blank" rel="noopener noreferrer">{eventTitle(next)}</a>
					{:else}{eventTitle(next)}{/if}
				</p>
				<p class="next__meta">
					<time datetime={next.date}>{weekday} {day} {monthLong} {year}</time>
					<span class="next__dot" aria-hidden="true">·</span>
					<span class="next__where">{eventWhere(next)}</span>
				</p>
				{#if next.url}
					<p class="next__cta">
						<a href={next.url} target="_blank" rel="noopener noreferrer">Tickets</a>
					</p>
				{/if}
			</div>
		</div>

		<Lineup lineup={next.lineup} prominent />

		<AddToCalendar event={next} />
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
	.next {
		margin: 2.5rem 0 3rem;
		padding: 1.4rem 1.6rem 1.6rem;
		border: 1px solid var(--rule);
		border-radius: 10px;
		background: var(--surface);
		box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
	}

	/* A solid rule across the top, so the box reads as the page's headline.
	   Monochrome throughout: the BMS logo is black-on-white, and the structure
	   does the work here rather than colour. */
	.next {
		position: relative;
		overflow: hidden;
	}

	.next::before {
		content: '';
		position: absolute;
		inset: 0 0 auto;
		height: 3px;
		background: var(--text);
	}

	.next__bar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		margin-bottom: 1rem;
	}

	.next__label {
		margin: 0;
		font-size: 0.72rem;
		font-weight: 700;
		letter-spacing: 0.16em;
		text-transform: uppercase;
		color: var(--text);
	}

	.next__countdown {
		padding: 0.2rem 0.6rem;
		border-radius: 999px;
		background: var(--text);
		color: var(--bg);
		font-size: 0.75rem;
		font-weight: 600;
		white-space: nowrap;
	}

	.next__head {
		display: flex;
		align-items: flex-start;
		gap: 1.1rem;
	}

	/* Calendar tile. */
	.next__date {
		flex: 0 0 auto;
		width: 4.2rem;
		padding: 0.5rem 0 0.6rem;
		border-radius: 8px;
		background: var(--bg);
		border: 1px solid var(--rule);
		text-align: center;
		line-height: 1;
	}

	.next__day {
		display: block;
		font-size: 1.9rem;
		font-weight: 700;
		font-variant-numeric: tabular-nums;
		letter-spacing: -0.02em;
	}

	.next__month {
		display: block;
		margin-top: 0.25rem;
		font-size: 0.72rem;
		font-weight: 700;
		letter-spacing: 0.12em;
		text-transform: uppercase;
		color: var(--text-muted);
	}

	.next__what {
		min-width: 0;
	}

	.next__title {
		margin: 0;
		font-size: 1.6rem;
		font-weight: 700;
		line-height: 1.15;
		letter-spacing: -0.015em;
	}

	.next__title a {
		text-decoration: none;
	}

	.next__title a:hover {
		text-decoration: underline;
	}

	.next__meta {
		margin: 0.35rem 0 0;
		color: var(--text-muted);
		font-size: 0.95rem;
	}

	.next__dot {
		margin: 0 0.3rem;
		opacity: 0.6;
	}

	.next__cta {
		margin: 0.8rem 0 0;
	}

	.next__cta a {
		display: inline-block;
		padding: 0.4rem 0.95rem;
		border-radius: 999px;
		background: var(--text);
		color: var(--bg);
		font-size: 0.88rem;
		font-weight: 600;
		text-decoration: none;
	}

	.next__cta a:hover {
		background: var(--text-muted);
	}

	.next--empty::before {
		background: var(--rule);
	}

	@media (max-width: 34rem) {
		.next {
			padding: 1.2rem 1.1rem 1.3rem;
		}

		.next__head {
			gap: 0.85rem;
		}

		.next__date {
			width: 3.6rem;
		}

		.next__day {
			font-size: 1.6rem;
		}

		.next__title {
			font-size: 1.3rem;
		}
	}
</style>
