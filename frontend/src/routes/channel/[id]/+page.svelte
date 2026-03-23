<script lang="ts">
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { getChannel, type ChannelDetail, type Conversation, getConversation } from '$lib/api';

	let channel = $state<ChannelDetail | null>(null);
	let convos = $state<Conversation[]>([]);

	$effect(() => {
		const id = page.params.id;
		if (id) loadChannel(id);
	});

	async function loadChannel(id: string) {
		channel = await getChannel(id);
		// Load conversation details
		const loaded = await Promise.all(
			channel.conversation_ids.map(async (cid) => {
				try {
					const c = await getConversation(cid);
					return { id: c.id, title: c.title, created_at: c.created_at, updated_at: c.updated_at, channel_ids: c.channel_ids } as Conversation;
				} catch {
					return null;
				}
			})
		);
		convos = loaded.filter((c): c is Conversation => c !== null);
	}
</script>

<div class="channel-view">
	{#if channel}
		<header>
			<h2>{channel.name}</h2>
			{#if channel.description}
				<p class="desc">{channel.description}</p>
			{/if}
		</header>

		<div class="conversations">
			{#each convos as conv (conv.id)}
				<a href="/conversation/{conv.id}" class="conv-card">
					<span class="conv-title">{conv.title || 'Untitled'}</span>
					<span class="conv-date">{new Date(conv.updated_at).toLocaleDateString()}</span>
				</a>
			{:else}
				<p class="empty">No conversations in this channel yet</p>
			{/each}
		</div>
	{:else}
		<div class="loading">Loading...</div>
	{/if}
</div>

<style>
	.channel-view {
		flex: 1;
		padding: 24px;
		overflow-y: auto;
	}

	header h2 {
		margin: 0 0 4px;
		font-size: 20px;
	}

	.desc {
		color: var(--text-secondary);
		font-size: 14px;
		margin: 0 0 24px;
	}

	.conversations {
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.conv-card {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 12px 16px;
		background: var(--bg-secondary);
		border-radius: 8px;
		text-decoration: none;
		color: var(--text);
		transition: background 0.1s;
	}

	.conv-card:hover {
		background: var(--bg-tertiary);
	}

	.conv-title {
		font-size: 14px;
	}

	.conv-date {
		font-size: 12px;
		color: var(--text-secondary);
	}

	.empty,
	.loading {
		text-align: center;
		color: var(--text-secondary);
		padding: 40px;
	}
</style>
