<script>
	/** `prominent` is the homepage billing: bigger type, a rule under each act. */
	let { lineup = [], prominent = false } = $props();

	// The early events were announced on a flyer as a list of names with no set
	// times. Rendered in the two-column grid they would each sit beside an empty
	// gutter, so a line-up with no times at all renders as a plain list.
	const hasTimes = $derived(lineup.some((a) => a.time));

	// Some events ran across several rooms; group so the room is stated once.
	const groups = $derived.by(() => {
		const out = [];
		for (const act of lineup) {
			const space = act.space ?? null;
			if (!out.length || out.at(-1).space !== space) out.push({ space, acts: [] });
			out.at(-1).acts.push(act);
		}
		return out;
	});
</script>

{#if lineup.length}
	<div class="lineup" class:lineup--prominent={prominent} class:lineup--untimed={!hasTimes}>
		{#each groups as group, i (i)}
			{#if group.space}<p class="lineup__space">{group.space}</p>{/if}
			<ol class="lineup__acts">
				<!-- Unkeyed on purpose. An act can legitimately appear twice on one
				     bill under the same name and time - sehrsehr opened and closed
				     BMS48 - and a duplicate key throws, taking the page down at
				     hydration while the server-rendered HTML looks fine. The list
				     is static, so there is nothing for a key to buy here. -->
				{#each group.acts as act}
					<li>
						{#if hasTimes}<span class="lineup__time">{act.time}</span>{/if}
						<span class="lineup__act">
							{#if act.url}
								<a href={act.url} target="_blank" rel="noopener noreferrer">{act.act}</a>
							{:else}{act.act}{/if}
							<!-- Acts with no site of their own get their Instagram handle instead.
							     A slot can hold two artists, so this is a list. -->
							{#each act.instagram ?? [] as handle}
								<a
									class="lineup__handle"
									href="https://www.instagram.com/{handle}/"
									target="_blank"
									rel="noopener noreferrer">@{handle}</a
								>
							{/each}
						</span>
					</li>
				{/each}
			</ol>
		{/each}
	</div>
{/if}

<style>
	.lineup {
		margin: 1rem 0;
	}

	/* A room name is a name - "Movement Space or Outside", not a shouted label. */
	.lineup__space {
		margin: 1rem 0 0.4rem;
		font-size: 0.95rem;
		font-weight: 600;
		color: var(--text-muted);
	}

	.lineup__acts {
		margin: 0;
		padding: 0;
		list-style: none;
	}

	.lineup__acts li {
		display: grid;
		grid-template-columns: 4.5rem 1fr;
		gap: 0 0.75rem;
		padding: 0.2rem 0;
	}

	.lineup__time {
		color: var(--text-muted);
		font-variant-numeric: tabular-nums;
		font-size: 0.9rem;
	}

	.lineup__act {
		font-weight: 600;
	}

	.lineup--untimed .lineup__acts li {
		grid-template-columns: 1fr;
	}

	.lineup__handle {
		margin-left: 0.45rem;
		color: var(--text-muted);
		font-weight: 400;
		font-size: 0.85em;
		text-decoration: none;
		white-space: nowrap;
	}

	.lineup__handle:hover {
		color: var(--text);
		text-decoration: underline;
	}

	/* Homepage billing. No rules between acts - the running order reads as a
	   list, and the tabular times already line it up. */
	.lineup--prominent .lineup__acts li {
		grid-template-columns: 5.5rem 1fr;
		padding: 0.3rem 0;
		align-items: baseline;
	}

	.lineup--prominent .lineup__time {
		font-size: 0.95rem;
		font-weight: 400;
		color: var(--text-muted);
	}

	.lineup--prominent .lineup__act {
		font-size: 0.95rem;
		font-weight: 700;
	}

	.lineup--prominent .lineup__space {
		margin-top: 1.2rem;
	}

	.lineup--prominent .lineup__space:first-child {
		margin-top: 0.5rem;
	}

	@media (max-width: 30rem) {
		.lineup--prominent .lineup__acts li {
			grid-template-columns: 4.2rem 1fr;
		}
	}
</style>
