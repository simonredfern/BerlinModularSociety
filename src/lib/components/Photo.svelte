<script>
	import { base } from '$app/paths';
	import photos from '$lib/data/photos.json';
	import sizes from '$lib/data/photo-sizes.json';

	let {
		id,
		sizes: sizesAttr = '(max-width: 46rem) 100vw, 46rem',
		zoom = true,
		/** No <figure>, caption or lightbox - just the image. For page furniture
		    like the header cover and logo, which are not part of the prose. */
		bare = false,
		/** Above-the-fold images should not be lazy. */
		eager = false
	} = $props();

	// Must be declared, or `bind:this` compiles to a bare global lookup and the
	// zoom button throws instead of opening the lightbox.
	let dialog = $state(null);

	// These throw during prerender, so a typo'd id fails `npm run build`
	// rather than shipping a broken image.
	const meta = $derived.by(() => {
		const m = photos[id];
		if (!m) throw new Error(`<Photo id="${id}"> - no such id in src/lib/data/photos.json`);
		return m;
	});

	const dim = $derived.by(() => {
		const d = sizes[id];
		if (!d) throw new Error(`<Photo id="${id}"> - no generated sizes. Run: npm run images`);
		return d;
	});

	const srcset = $derived(
		(ext) => dim.widths.map((w) => `${base}/images/${id}-${w}.${ext} ${w}w`).join(', ')
	);
	const full = $derived(`${base}/images/${id}-${dim.widths[dim.widths.length - 1]}.${dim.ext}`);
	const hasCaption = $derived(Boolean(meta.captionHtml || meta.credit));
</script>

{#snippet picture()}
	<picture>
		<source type="image/avif" srcset={srcset('avif')} sizes={sizesAttr} />
		<source type="image/webp" srcset={srcset('webp')} sizes={sizesAttr} />
		<img
			src={full}
			srcset={srcset(dim.ext)}
			sizes={sizesAttr}
			width={dim.width}
			height={dim.height}
			alt={meta.alt}
			loading={eager ? 'eager' : 'lazy'}
			decoding="async"
		/>
	</picture>
{/snippet}

{#if bare}
	{@render picture()}
{:else}
<figure class="photo">
	{#if zoom}
		<button
			type="button"
			class="photo__zoom"
			onclick={() => dialog?.showModal()}
			aria-label={`Enlarge: ${meta.alt || id}`}
		>
			<picture>
				<source type="image/avif" srcset={srcset('avif')} sizes={sizesAttr} />
				<source type="image/webp" srcset={srcset('webp')} sizes={sizesAttr} />
				<img
					src={full}
					srcset={srcset(dim.ext)}
					sizes={sizesAttr}
					width={dim.width}
					height={dim.height}
					alt={meta.alt}
					loading="lazy"
					decoding="async"
				/>
			</picture>
		</button>
	{:else}
		<picture>
			<source type="image/avif" srcset={srcset('avif')} sizes={sizesAttr} />
			<source type="image/webp" srcset={srcset('webp')} sizes={sizesAttr} />
			<img
				src={full}
				srcset={srcset(dim.ext)}
				sizes={sizesAttr}
				width={dim.width}
				height={dim.height}
				alt={meta.alt}
				loading="lazy"
				decoding="async"
			/>
		</picture>
	{/if}

	{#if hasCaption}
		<figcaption>
			{#if meta.captionHtml}<span class="photo__caption">{@html meta.captionHtml}</span>{/if}
			{#if meta.credit}
				<span class="photo__credit">
					Photo:
					{#if meta.creditUrl}
						<a href={meta.creditUrl} target="_blank" rel="noopener noreferrer">{meta.credit}</a>
					{:else}{meta.credit}{/if}
				</span>
			{/if}
		</figcaption>
	{/if}
</figure>
{/if}

{#if zoom && !bare}
	<dialog bind:this={dialog} class="lightbox" onclick={() => dialog?.close()}>
		<img src={full} alt={meta.alt} />
		{#if hasCaption}
			<p class="lightbox__caption">
				{#if meta.captionHtml}{@html meta.captionHtml}{/if}
				{#if meta.credit}<span class="photo__credit">Photo: {meta.credit}</span>{/if}
			</p>
		{/if}
	</dialog>
{/if}

<style>
	.photo {
		margin: 2rem 0;
	}

	.photo :global(img) {
		display: block;
		width: 100%;
		height: auto;
		border-radius: 2px;
		background: var(--surface);
	}

	.photo__zoom {
		display: block;
		width: 100%;
		padding: 0;
		border: 0;
		background: none;
		cursor: zoom-in;
	}

	.photo__zoom:focus-visible {
		outline: 2px solid var(--accent);
		outline-offset: 3px;
	}

	figcaption {
		margin-top: 0.6rem;
		font-size: 0.85rem;
		line-height: 1.5;
		color: var(--text-muted);
	}

	.photo__credit {
		display: inline-block;
		font-style: italic;
		opacity: 0.85;
	}

	.photo__caption + .photo__credit::before {
		content: '· ';
		font-style: normal;
	}

	.lightbox {
		max-width: min(96vw, 1920px);
		max-height: 94vh;
		padding: 0;
		border: 0;
		background: transparent;
		overflow: hidden;
	}

	.lightbox::backdrop {
		background: rgb(0 0 0 / 0.88);
	}

	.lightbox img {
		display: block;
		max-width: 100%;
		max-height: 84vh;
		width: auto;
		height: auto;
		margin: 0 auto;
		cursor: zoom-out;
	}

	.lightbox__caption {
		margin: 0.75rem 0 0;
		color: #ddd;
		font-size: 0.85rem;
		text-align: center;
	}
</style>
