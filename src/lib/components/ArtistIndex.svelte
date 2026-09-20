<script>
	import { base } from '$app/paths';
	import artists from '$lib/data/artists.json';
	import events from '$lib/data/events.json';
	import { formatEventDate, eventWhere, splitEvents } from '$lib/events.js';

	// The index is a record of what has happened, so it counts archive events only.
	// An announced line-up is not yet a performance - and it also keeps every link
	// here pointing at /event-archive, where an upcoming event has no anchor.
	const split = splitEvents();
	const archive = [...split.past, ...split.undated];
	const inArchive = new Set(archive.map((e) => e.number));

	/**
	 * Everyone who has played BMS, and when.
	 *
	 * Built from the `artists` slugs on each act rather than from the act names, so
	 * the twenty-odd spellings of drusnoise and the b2b billings all land on one
	 * entry. The per-appearance handles stay in events.json - a website an artist
	 * had in 2022 is part of that night's record even after it moves.
	 */
	const index = $derived.by(() => {
		const appearances = new Map();
		for (const e of events) {
			if (!inArchive.has(e.number)) continue;
			for (const act of e.lineup) {
				for (const slug of act.artists ?? []) {
					if (!appearances.has(slug)) appearances.set(slug, []);
					appearances.get(slug).push({ event: e, billed: act.act });
				}
			}
		}

		const rows = [...appearances].map(([slug, list]) => {
			// An artist can appear twice on one bill under the same name - sehrsehr
			// opened and closed BMS48. Collapse those: the reader wants the event
			// once. A different billing on the same night is kept, because it says
			// something (3rd Party Influence's "2nd set").
			const once = new Map();
			for (const ap of list) {
				const id = `${ap.event.number}|${ap.billed}`;
				once.set(id, { ...ap, id });
			}
			return {
				...(artists[slug] ?? { slug, name: slug }),
				slug,
				// Newest first, the way the archive reads.
				list: [...once.values()].sort((a, b) => b.event.date.localeCompare(a.event.date))
			};
		});

		// Strip diacritics, or "Éira" sorts among the E's but groups under "#",
		// which splits the alphabet into duplicate headings.
		const sortKey = (n) =>
			n
				.normalize('NFD')
				.replace(/[\u0300-\u036f]/g, '')
				.replace(/^[^\p{L}\p{N}]+/u, '')
				.toLowerCase();
		rows.sort((a, b) => sortKey(a.name).localeCompare(sortKey(b.name)));

		const groups = [];
		for (const r of rows) {
			const ch = sortKey(r.name)[0]?.toUpperCase() ?? '#';
			const letter = /[A-Z]/.test(ch) ? ch : '#';
			if (!groups.length || groups.at(-1).letter !== letter) groups.push({ letter, rows: [] });
			groups.at(-1).rows.push(r);
		}
		return { rows, groups };
	});

	const when = (e) => formatEventDate(new Date(`${e.date}T00:00:00`));
</script>

<p class="summary">
	<strong>{index.rows.length}</strong> artists have played Berlin Modular Society across
	<strong>{archive.length}</strong> events.
</p>

<nav class="jump" aria-label="Jump to letter">
	{#each index.groups as g (g.letter)}
		<a href="#letter-{g.letter}">{g.letter}</a>
	{/each}
</nav>

{#each index.groups as g (g.letter)}
	<h2 id="letter-{g.letter}" class="letter">{g.letter}</h2>

	<ul class="artists">
		{#each g.rows as a (a.slug)}
			<li class="artist" id="artist-{a.slug}">
				<p class="artist__name">
					{#if a.url}
						<a href={a.url} target="_blank" rel="noopener noreferrer">{a.name}</a>
					{:else}{a.name}{/if}
					{#if a.aka?.length}
						<span class="artist__aka">aka {a.aka.join(', ')}</span>
					{/if}
					{#each a.instagram ?? [] as h}
						<a
							class="artist__handle"
							href="https://www.instagram.com/{h}/"
							target="_blank"
							rel="noopener noreferrer">@{h}</a
						>
					{/each}
				</p>

				<ul class="artist__gigs">
					{#each a.list as ap (ap.id)}
						<li>
							<a href="{base}/event-archive#{ap.event.slug}">{ap.event.number}</a>
							<span class="artist__when">{when(ap.event)}</span>
							{#if ap.event.venue}<span class="artist__where">{eventWhere(ap.event)}</span>{/if}
							{#if ap.billed !== a.name}<span class="artist__billed">billed as {ap.billed}</span>{/if}
						</li>
					{/each}
				</ul>
			</li>
		{/each}
	</ul>
{/each}

<style>
	.summary {
		margin: 0 0 1.5rem;
		color: var(--text-muted);
	}

	.jump {
		display: flex;
		flex-wrap: wrap;
		gap: 0.3rem 0.5rem;
		margin-bottom: 2rem;
		padding-bottom: 1rem;
		border-bottom: 1px solid var(--rule);
	}

	.jump a {
		min-width: 1.5rem;
		padding: 0.1rem 0.3rem;
		border: 1px solid var(--rule);
		border-radius: 3px;
		text-align: center;
		text-decoration: none;
		font-size: 0.85rem;
		font-variant-numeric: tabular-nums;
	}

	.jump a:hover {
		border-color: var(--text);
	}

	.letter {
		margin: 2.5rem 0 0.75rem;
		font-size: 0.8rem;
		font-weight: 700;
		letter-spacing: 0.18em;
		color: var(--text-muted);
	}

	.artists {
		margin: 0;
		padding: 0;
		list-style: none;
	}

	.artist {
		padding: 0.7rem 0;
		border-top: 1px solid var(--rule);
	}

	.artist__name {
		margin: 0 0 0.25rem;
		font-weight: 600;
	}

	.artist__aka {
		margin-left: 0.45rem;
		color: var(--text-muted);
		font-weight: 400;
		font-size: 0.85em;
	}

	.artist__handle {
		margin-left: 0.45rem;
		color: var(--text-muted);
		font-weight: 400;
		font-size: 0.85em;
		text-decoration: none;
	}

	.artist__handle:hover {
		color: var(--text);
		text-decoration: underline;
	}

	.artist__gigs {
		margin: 0;
		padding: 0;
		list-style: none;
		font-size: 0.9rem;
		color: var(--text-muted);
	}

	.artist__gigs li {
		display: flex;
		flex-wrap: wrap;
		gap: 0 0.5rem;
		padding: 0.1rem 0;
	}

	.artist__gigs a {
		font-weight: 600;
		font-variant-numeric: tabular-nums;
		text-decoration: none;
		min-width: 4rem;
	}

	.artist__gigs a:hover {
		text-decoration: underline;
	}

	.artist__when {
		min-width: 12rem;
	}

	.artist__billed {
		font-style: italic;
		opacity: 0.8;
	}

	@media (max-width: 34rem) {
		.artist__when {
			min-width: 0;
		}
	}
</style>
