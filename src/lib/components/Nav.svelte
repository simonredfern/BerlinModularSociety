<script>
	import { base } from '$app/paths';
	import { page } from '$app/state';
	import nav from '$lib/data/nav.json';

	let open = $state(false);
	const current = $derived(page.url.pathname);
</script>

<header class="site-header">
	<div class="site-header__bar">
		<a class="brand" href="{base}/" onclick={() => (open = false)}>
			<img src="{base}/favicon.png" alt="" width="26" height="26" />
			<span>Berlin Modular Society</span>
		</a>

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

	.site-header__bar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		max-width: var(--measure);
		margin: 0 auto;
		padding: 0.7rem 1rem;
	}

	.brand {
		display: inline-flex;
		align-items: center;
		gap: 0.55rem;
		color: var(--text);
		font-weight: 600;
		font-size: 0.95rem;
		text-decoration: none;
		white-space: nowrap;
	}

	.brand img {
		border-radius: 3px;
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
		padding: 0 1rem 0.65rem;
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
