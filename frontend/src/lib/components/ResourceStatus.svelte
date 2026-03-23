<script lang="ts">
	interface Props {
		url: string;
		type: string;
	}

	let { url, type }: Props = $props();
</script>

<div class="resource-status">
	<span class="indicator"></span>
	<span class="label">Processing {type}: {url}</span>
</div>

<style>
	.resource-status {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 6px 12px;
		font-size: 12px;
		color: var(--text-secondary);
		background: var(--bg-secondary);
		border-radius: 8px;
		margin: 4px 0;
	}

	.indicator {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background: var(--accent);
		animation: pulse 1.5s infinite;
	}

	@keyframes pulse {
		0%, 100% { opacity: 1; }
		50% { opacity: 0.3; }
	}
</style>
