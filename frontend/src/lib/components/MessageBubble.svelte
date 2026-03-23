<script lang="ts">
	import CogTag from './CogTag.svelte';
	import { marked } from 'marked';
	import type { Message } from '$lib/api';

	interface Props {
		message: Message;
	}

	let { message }: Props = $props();

	let html = $derived(
		message.role === 'assistant'
			? marked.parse(message.content, { async: false }) as string
			: ''
	);
</script>

<div class="message {message.role}">
	<div class="bubble">
		{#if message.role === 'assistant'}
			<div class="markdown">{@html html}</div>
		{:else}
			<p>{message.content}</p>
		{/if}
	</div>
	{#if message.cognitive_operations && message.cognitive_operations.length > 0}
		<div class="cog-tags">
			{#each message.cognitive_operations as tag}
				<CogTag {tag} />
			{/each}
		</div>
	{/if}
</div>

<style>
	.message {
		padding: 4px 0;
		max-width: 80%;
	}

	.message.user {
		margin-left: auto;
	}

	.message.assistant {
		margin-right: auto;
	}

	.bubble {
		padding: 10px 14px;
		border-radius: 16px;
		font-size: 14px;
		line-height: 1.6;
	}

	.user .bubble {
		background: var(--accent);
		color: white;
		border-bottom-right-radius: 4px;
	}

	.assistant .bubble {
		background: var(--bg-secondary);
		color: var(--text);
		border-bottom-left-radius: 4px;
	}

	.bubble p {
		margin: 0;
		white-space: pre-wrap;
	}

	.cog-tags {
		margin-top: 4px;
		padding-left: 4px;
	}

	.markdown :global(p) {
		margin: 0 0 8px;
	}

	.markdown :global(p:last-child) {
		margin-bottom: 0;
	}

	.markdown :global(pre) {
		background: var(--bg-tertiary);
		padding: 10px;
		border-radius: 8px;
		overflow-x: auto;
		font-size: 13px;
	}

	.markdown :global(code) {
		font-size: 13px;
	}

	.markdown :global(ul),
	.markdown :global(ol) {
		margin: 4px 0;
		padding-left: 20px;
	}
</style>
