<script>
	/**
	 * A block of Notion-coloured content.
	 *
	 * Inline colour is just a <span class="nc-*"> in the markdown, but a whole
	 * coloured paragraph cannot be: mdsvex treats a line that opens with a tag as
	 * raw HTML and stops parsing markdown inside it, so the bold and the links
	 * come out as literal asterisks and brackets. Wrapped in a component with
	 * blank lines around the content, the markdown is parsed as usual.
	 */
	let { c, children } = $props();
</script>

<div class="nc-{c}">{@render children?.()}</div>

<style>
	div :global(p:first-child) {
		margin-top: 0;
	}

	div :global(p:last-child) {
		margin-bottom: 0;
	}
</style>
