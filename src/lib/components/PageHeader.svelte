<script>
	import Photo from '$lib/components/Photo.svelte';

	/** The Super page header: a wide cover photo, the BMS logo, and the title. */
	/**
	 * The banner every page wears unless it brings its own. Only the homepage,
	 * /event-archive and /artist-area/artist-payments set `cover` in their
	 * frontmatter; the rest inherit this so the site reads as one thing.
	 * A page can opt out with `cover: ""`.
	 */
	const DEFAULT_COVER = 'bms_dsc-1652-2-crop-banner';

	/**
	 * Likewise the logo. Most migrated pages carry this exact id already; pages
	 * added since had none, which left them without the mark every other page
	 * wears. Opt out with `icon: ""`.
	 */
	const DEFAULT_ICON = 'bms_logo-in-black-on-white-background';

	/** `titleHidden` keeps the heading in the DOM but out of sight - for a page
	    whose logo image already is the wordmark. */
	let { title, cover = null, icon = null, level = 1, titleHidden = false } = $props();

	const banner = $derived(cover === '' ? null : (cover ?? DEFAULT_COVER));
	const mark = $derived(icon === '' ? null : (icon ?? DEFAULT_ICON));
</script>

<header class="page-header" class:page-header--cover={banner}>
	{#if banner}
		<div class="page-header__cover">
			<Photo id={banner} bare eager sizes="100vw" />
		</div>
	{/if}

	{#if mark}
		<div class="page-header__icon">
			<Photo id={mark} bare eager sizes="5rem" />
		</div>
	{/if}

	{#if level === 1}
		<h1 class="page-header__title" class:sr-only={titleHidden}>{title}</h1>
	{:else}
		<p class="page-header__title" class:sr-only={titleHidden}>{title}</p>
	{/if}
</header>

<style>
	.page-header {
		margin-bottom: 2rem;
	}

	/* The cover bleeds past the prose measure to the full page width, as it did
	   on the old site. Negative margins rather than width:100vw - setting both
	   double-counts and pushes the image off to one side. `display: flex` was
	   worse still: <picture> became a flex item and shrank to nothing, which is
	   why the banner first appeared as a sliver in the left margin. */
	.page-header__cover {
		margin-top: -2.5rem;
		margin-left: calc(50% - 50vw);
		margin-right: calc(50% - 50vw);
		overflow: hidden;
	}

	.page-header__cover :global(picture) {
		display: block;
	}

	.page-header__cover :global(img) {
		width: 100%;
		height: clamp(9rem, 30vh, 20rem);
		object-fit: cover;
		display: block;
	}

	.page-header__icon {
		width: 5rem;
		height: 5rem;
		margin-bottom: 0.75rem;
		border-radius: 6px;
		overflow: hidden;
		background: var(--bg);
	}

	/* Pulled up so it straddles the cover edge, the way Notion places it. */
	.page-header--cover .page-header__icon {
		margin-top: -2.5rem;
		position: relative;
		box-shadow: 0 0 0 3px var(--bg);
	}

	.page-header__icon :global(img) {
		width: 100%;
		height: 100%;
		object-fit: contain;
		display: block;
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

	.page-header__title {
		margin: 0;
		font-size: 2.1rem;
		font-weight: 700;
		line-height: 1.15;
	}

	@media (max-width: 34rem) {
		.page-header__cover :global(img) {
			height: clamp(7rem, 22vh, 12rem);
		}

		.page-header__icon {
			width: 4rem;
			height: 4rem;
		}

		.page-header__title {
			font-size: 1.7rem;
		}
	}
</style>
