<script>
	import { base } from '$app/paths';
	import { page } from '$app/state';
	import nav from '$lib/data/nav.json';

	let open = $state(false);
	const current = $derived(page.url.pathname);
</script>

<header class="site-header">
	<div class="site-header__bar">
		<button
			class="nav-toggle"
			type="button"
			aria-expanded={open}
			aria-controls="site-nav"
			onclick={() => (open = !open)}
		>
			{open ? 'Close' : 'Menu'}
		</button>
	</div>

	<nav id="site-nav" class="site-nav" class:site-nav--open={open} aria-label="Main">
		<ul>
			{#each nav as item (item.slug)}
				<li>
					<a
						href="{base}/{item.slug}"
						aria-current={current === `${base}/${item.slug}` ? 'page' : undefined}
						onclick={() => (open = false)}
					>
						{item.short}
					</a>
				</li>
			{/each}
		</ul>
	</nav>
</header>

<style>
	.site-header {
		position: sticky;
		top: 0;
		z-index: 10;
		background: color-mix(in srgb, var(--bg) 92%, transparent);
		backdrop-filter: blur(8px);
		border-bottom: 1px solid var(--rule);
	}

	/* Holds nothing but the mobile menu toggle now that the brand is gone, so it
	   is not rendered at all on wider screens. */
	.site-header__bar {
		display: none;
	}

				.nav-toggle {
		display: none;
		padding: 0.35rem 0.7rem;
		border: 1px solid var(--rule);
		border-radius: 3px;
		background: var(--surface);
		color: var(--text);
		font: inherit;
		font-size: 0.85rem;
		cursor: pointer;
	}

	.site-nav ul {
		display: flex;
		flex-wrap: wrap;
		gap: 0.15rem 1rem;
		max-width: var(--measure);
		margin: 0 auto;
		/* The brand bar used to provide the space above these links. */
		padding: 0.8rem 1rem 0.7rem;
		list-style: none;
	}

	.site-nav a {
		color: var(--text-muted);
		font-size: 0.85rem;
		text-decoration: none;
	}

	.site-nav a:hover,
	.site-nav a[aria-current='page'] {
		color: var(--text);
	}

	.site-nav a[aria-current='page'] {
		font-weight: 600;
	}

	@media (max-width: 40rem) {
		.site-header__bar {
			display: flex;
			justify-content: flex-end;
			max-width: var(--measure);
			margin: 0 auto;
			padding: 0.6rem 1rem;
		}

		.nav-toggle {
			display: block;
		}

		.site-nav {
			display: none;
		}

		.site-nav--open {
			display: block;
		}

		.site-nav ul {
			flex-direction: column;
			gap: 0;
			/* The toggle bar sits above on mobile, so no extra space is needed. */
			padding-top: 0;
			padding-bottom: 0.75rem;
		}

		.site-nav li {
			border-top: 1px solid var(--rule);
		}

		.site-nav a {
			display: block;
			padding: 0.6rem 0;
			font-size: 0.95rem;
		}
	}
</style>
