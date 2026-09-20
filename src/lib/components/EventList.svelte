<script>
	import { onMount } from 'svelte';
	import { splitEvents, formatEventDate, eventTitle, eventWhereLong } from '$lib/events.js';

	/** 'upcoming' or 'past'. The compact view - the archive uses EventArchive. */
	let { show = 'upcoming' } = $props();

	let now = $state(new Date());
	const split = $derived(splitEvents(now));
	const list = $derived(show === 'upcoming' ? split.upcoming : split.past);

	onMount(() => {
		now = new Date();
	});
</script>

{#if list.length}
	<ul class="events">
		{#each list as e (e.number)}
			<li class="event">
				<time class="event__date" datetime={e.date}>{formatEventDate(e.when)}</time>
				<div>
					<span class="event__what">
						{#if e.url}
							<a href={e.url} target="_blank" rel="noopener noreferrer">{eventTitle(e)}</a>
						{:else}{eventTitle(e)}{/if}
					</span>
					<span class="event__where">{eventWhereLong(e)}</span>
				</div>
			</li>
		{/each}
	</ul>
{:else}
	<p>Nothing listed yet. We host events roughly monthly — check back, or follow us.</p>
{/if}

<style>
	.events {
		margin: 2rem 0;
		padding: 0;
		list-style: none;
	}

	.event {
		display: grid;
		grid-template-columns: 15rem 1fr;
		gap: 0 1.5rem;
		padding: 1rem 0;
		border-top: 1px solid var(--rule);
	}

	.event:last-child {
		border-bottom: 1px solid var(--rule);
	}

	.event__date {
		color: var(--text-muted);
		font-variant-numeric: tabular-nums;
		font-size: 0.9rem;
		padding-top: 0.15rem;
	}

	.event__what {
		display: block;
		font-weight: 600;
	}

	.event__where {
		display: block;
		margin-top: 0.2rem;
		color: var(--text-muted);
		font-size: 0.9rem;
	}

	@media (max-width: 38rem) {
		.event {
			grid-template-columns: 1fr;
			gap: 0.3rem;
		}
	}
</style>
