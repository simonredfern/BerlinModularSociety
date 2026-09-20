<script>
	import { base } from '$app/paths';
	import links from '$lib/data/links.json';
	import nav from '$lib/data/nav.json';

	const socials = [
		['Instagram', links.instagram],
		['Facebook', links.facebook],
		['Twitch', links.twitch],
		['YouTube', links.youtube],
		['Resident Advisor', links.residentAdvisor]
	];
</script>

<footer class="site-footer">
	<div class="site-footer__inner">
		<section>
			<h2>Pages</h2>
			<ul>
				{#each nav as item (item.slug)}
					<li><a href="{base}/{item.slug}">{item.title}</a></li>
				{/each}
			</ul>
		</section>

		<section>
			<h2>Streams + socials</h2>
			<ul>
				{#each socials as [label, href] (href)}
					<li><a {href} target="_blank" rel="noopener noreferrer">{label}</a></li>
				{/each}
			</ul>
		</section>

		<section>
			<h2>Get in touch</h2>
			<p>
				To perform, use the
				<a href="{base}/submit">artist submission page</a>.
			</p>
			<p>
				Anything else: <a href="mailto:{links.email}">{links.email}</a>
			</p>
			<p>
				<a href={links.mailingList} target="_blank" rel="noopener noreferrer">Join the mailing list</a>
			</p>
			<p class="co2">
				Travelling to us? Please come by train rather than plane — there is no Planet&nbsp;B.
			</p>
		</section>
	</div>

	<p class="site-footer__legal">
		Berlin Modular Society · Live modular music events · Berlin
	</p>
</footer>

<style>
	.site-footer {
		margin-top: 4rem;
		padding: 2.5rem 1rem 2rem;
		border-top: 1px solid var(--rule);
		background: var(--surface);
		font-size: 0.9rem;
	}

	.site-footer__inner {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(13rem, 1fr));
		gap: 2rem;
		max-width: var(--measure);
		margin: 0 auto;
	}

	h2 {
		margin: 0 0 0.6rem;
		font-size: 0.95rem;
		font-weight: 600;
		color: var(--text-muted);
	}

	ul {
		margin: 0;
		padding: 0;
		list-style: none;
	}

	li {
		margin-bottom: 0.3rem;
	}

	p {
		margin: 0 0 0.6rem;
	}

	.co2 {
		color: var(--text-muted);
	}

	.site-footer__legal {
		max-width: var(--measure);
		margin: 2.5rem auto 0;
		padding-top: 1.25rem;
		border-top: 1px solid var(--rule);
		color: var(--text-muted);
		font-size: 0.8rem;
	}
</style>
