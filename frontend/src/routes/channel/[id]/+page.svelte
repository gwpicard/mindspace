<script lang="ts">
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { getChannel, updateChannel, type ChannelDetail, type Conversation, getConversation } from '$lib/api';
	import { removeChannel, loadChannels } from '$lib/stores/channels';

	let channel = $state<ChannelDetail | null>(null);
	let convos = $state<Conversation[]>([]);
	let confirmingDelete = $state(false);
	let editing = $state(false);
	let editName = $state('');

	$effect(() => {
		const id = page.params.id;
		if (id) loadChannelData(id);
	});

	async function loadChannelData(id: string) {
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

	async function handleDelete() {
		if (!channel) return;
		if (confirmingDelete) {
			await removeChannel(channel.id);
			goto('/');
		} else {
			confirmingDelete = true;
		}
	}

	function startEdit() {
		if (!channel) return;
		editing = true;
		editName = channel.name;
	}

	async function saveEdit() {
		if (!channel || !editName.trim()) return;
		await updateChannel(channel.id, { name: editName.trim() });
		await loadChannelData(channel.id);
		await loadChannels();
		editing = false;
	}

	function cancelEdit() {
		editing = false;
	}

	function handleEditKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter') saveEdit();
		else if (e.key === 'Escape') cancelEdit();
	}
</script>

<div class="channel-view">
	{#if channel}
		<header>
			<div class="header-row">
				{#if editing}
					<input
						class="edit-input"
						data-testid="channel-name-input"
						bind:value={editName}
						onkeydown={handleEditKeydown}
						autofocus
					/>
				{:else}
					<h2 onclick={startEdit} class="editable">{channel.name}</h2>
					<button class="icon-btn" data-testid="edit-channel" onclick={startEdit} title="Edit name">
						<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
							<path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
						</svg>
					</button>
				{/if}
				<button
					class="icon-btn delete-btn"
					class:confirm={confirmingDelete}
					data-testid="delete-channel"
					onclick={handleDelete}
					title={confirmingDelete ? 'Click again to confirm' : 'Delete channel'}
				>
					{confirmingDelete ? '?' : '×'}
				</button>
			</div>
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

	.header-row {
		display: flex;
		align-items: center;
		gap: 8px;
	}

	header h2 {
		margin: 0;
		font-size: 20px;
	}

	h2.editable {
		cursor: pointer;
	}

	h2.editable:hover {
		text-decoration: underline;
		text-decoration-style: dotted;
	}

	.edit-input {
		font-size: 20px;
		font-weight: bold;
		border: 1px solid var(--border);
		border-radius: 6px;
		padding: 2px 8px;
		background: var(--bg-secondary);
		color: var(--text);
		outline: none;
	}

	.edit-input:focus {
		border-color: var(--accent);
	}

	.icon-btn {
		width: 28px;
		height: 28px;
		border-radius: 6px;
		border: none;
		background: transparent;
		color: var(--text-secondary);
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 18px;
	}

	.icon-btn:hover {
		background: var(--bg-tertiary);
		color: var(--text);
	}

	.delete-btn:hover {
		color: #ef4444;
	}

	.delete-btn.confirm {
		color: #ef4444;
		background: rgba(239, 68, 68, 0.1);
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
