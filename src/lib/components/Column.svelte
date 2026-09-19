<script>
	let { children } = $props();
</script>

<div class="column">{@render children?.()}</div>

<style>
	.column {
		min-width: 0;
	}
</style>
