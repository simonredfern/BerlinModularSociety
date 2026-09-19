<script>
	let { src, title = '', ratio = null } = $props();

	// Audio players are short and fixed-height; video wants 16:9.
	const AUDIO = /soundcloud\.com|bandcamp\.com|mixcloud\.com/;
	const kind = $derived(AUDIO.test(src) ? 'audio' : 'video');
	const aspect = $derived(ratio ?? (kind === 'video' ? '16 / 9' : null));

	function label(u) {
		try {
			return new URL(u).hostname.replace(/^www\./, '');
		} catch {
			return 'embed';
		}
	}
</script>

<div class="embed embed--{kind}" style={aspect ? `aspect-ratio: ${aspect}` : null}>
	<iframe
		{src}
		title={title || label(src)}
		loading="lazy"
		allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
		allowfullscreen
		referrerpolicy="strict-origin-when-cross-origin"
	></iframe>
</div>

<style>
	.embed {
		margin: 2rem 0;
		width: 100%;
		background: var(--surface);
		border-radius: 2px;
		overflow: hidden;
	}

	.embed--audio {
		height: 166px;
	}

	.embed iframe {
		display: block;
		width: 100%;
		height: 100%;
		border: 0;
	}
</style>
