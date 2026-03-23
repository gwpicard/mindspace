<script lang="ts">
	interface Props {
		tag: string;
	}

	let { tag }: Props = $props();
</script>

<span class="cog-tag">{tag}</span>

<style>
	.cog-tag {
		display: inline-block;
		padding: 1px 8px;
		border-radius: 10px;
		font-size: 11px;
		background: var(--bg-tertiary);
		color: var(--text-secondary);
		margin-right: 4px;
	}
</style>
