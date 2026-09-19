<script>
	let { children } = $props();
</script>

<div class="columns">{@render children?.()}</div>

<style>
	.columns {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(min(100%, 18rem), 1fr));
		gap: 0 1.5rem;
		align-items: start;
	}
</style>
