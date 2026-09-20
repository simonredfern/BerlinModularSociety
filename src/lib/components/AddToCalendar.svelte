<script>
	import { base } from '$app/paths';
	import { googleCalendarUrl } from '$lib/calendar.js';

	let { event } = $props();

	const google = $derived(googleCalendarUrl(event));
	const ics = $derived(`${base}/calendar/${event.slug}.ics`);
</script>

<div class="cal">
	<span class="cal__label">Add to calendar</span>
	<a class="cal__btn" href={google} target="_blank" rel="noopener noreferrer">Google</a>
	<a class="cal__btn" href={ics} download="{event.slug}.ics">Apple / Outlook / Thunderbird</a>
</div>

<style>
	.cal {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.4rem 0.5rem;
		margin-top: 1.1rem;
		padding-top: 1rem;
		border-top: 1px solid var(--rule);
	}

	.cal__label {
		margin-right: 0.2rem;
		font-size: 0.9rem;
		color: var(--text-muted);
	}

	.cal__btn {
		padding: 0.3rem 0.7rem;
		border: 1px solid var(--rule);
		border-radius: 999px;
		background: var(--bg);
		color: var(--text);
		font-size: 0.85rem;
		font-weight: 600;
		text-decoration: none;
	}

	.cal__btn:hover {
		border-color: var(--text);
	}
</style>
