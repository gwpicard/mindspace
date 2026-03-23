<script lang="ts">
	import { conversations, loadConversations, removeConversation } from '$lib/stores/conversations';
	import { channels, loadChannels } from '$lib/stores/channels';
	import { resources, loadResources } from '$lib/stores/resources';
	import { searchOpen } from '$lib/stores/search';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { onMount } from 'svelte';

	let tab = $state<'conversations' | 'channels' | 'library'>('conversations');

	onMount(() => {
		loadConversations();
		loadChannels();
		loadResources();
	});

	function newConversation() {
		goto('/');
	}

	function openSearch() {
		searchOpen.set(true);
	}

	const TYPE_LABELS: Record<string, string> = {
		repo: 'Repo',
		url: 'Article',
		snippet: 'Snippet',
		video: 'Video',
		note: 'Note',
		thought: 'Thought',
	};

	const TYPE_COLORS: Record<string, string> = {
		repo: '#8b5cf6',
		url: '#3b82f6',
		snippet: '#f59e0b',
		video: '#ef4444',
		note: '#10b981',
		thought: '#6366f1',
	};

	function formatDate(iso: string): string {
		const d = new Date(iso);
		const now = new Date();
		if (d.toDateString() === now.toDateString()) {
			return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
		}
		return d.toLocaleDateString([], { month: 'short', day: 'numeric' });
	}
</script>

<aside class="sidebar">
	<div class="sidebar-header">
		<h1 class="logo">mindspace</h1>
		<div class="header-actions">
			<button class="icon-btn" onclick={openSearch} title="Search (Cmd+K)">
				<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<circle cx="11" cy="11" r="8"></circle>
					<line x1="21" y1="21" x2="16.65" y2="16.65"></line>
				</svg>
			</button>
			<button class="icon-btn" onclick={newConversation} title="New conversation">
				<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<line x1="12" y1="5" x2="12" y2="19"></line>
					<line x1="5" y1="12" x2="19" y2="12"></line>
				</svg>
			</button>
		</div>
	</div>

	<div class="tabs">
		<button class:active={tab === 'conversations'} onclick={() => (tab = 'conversations')}>
			Conversations
		</button>
		<button class:active={tab === 'channels'} onclick={() => (tab = 'channels')}>
			Channels
		</button>
		<button class:active={tab === 'library'} onclick={() => (tab = 'library')}>
			Library
		</button>
	</div>

	<nav class="list">
		{#if tab === 'conversations'}
			{#each $conversations as conv (conv.id)}
				{@const active = page.url.pathname === `/conversation/${conv.id}`}
				<a href="/conversation/{conv.id}" class="item" class:active>
					<span class="item-title">{conv.title || 'Untitled'}</span>
					<span class="item-date">{formatDate(conv.updated_at)}</span>
				</a>
			{/each}
			{#if $conversations.length === 0}
				<p class="empty">No conversations yet</p>
			{/if}
		{:else if tab === 'channels'}
			{#each $channels as chan (chan.id)}
				<a href="/channel/{chan.id}" class="item">
					<span class="item-title">{chan.name}</span>
				</a>
			{/each}
			{#if $channels.length === 0}
				<p class="empty">No channels yet</p>
			{/if}
		{:else}
			{#each $resources as res (res.id)}
				{@const active = page.url.pathname === `/resource/${res.id}`}
				<a href="/resource/{res.id}" class="item" class:active>
					<span class="item-title">{res.title || res.source_url || 'Untitled'}</span>
					<span class="item-meta">
						<span class="type-badge" style="--type-color: {TYPE_COLORS[res.type] || '#888'}">{TYPE_LABELS[res.type] || res.type}</span>
						<span class="item-date">{formatDate(res.created_at)}</span>
					</span>
				</a>
			{/each}
			{#if $resources.length === 0}
				<p class="empty">No resources yet</p>
			{/if}
		{/if}
	</nav>
</aside>

<style>
	.sidebar {
		width: 260px;
		height: 100vh;
		display: flex;
		flex-direction: column;
		border-right: 1px solid var(--border);
		background: var(--bg-secondary);
	}

	.sidebar-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 16px;
		border-bottom: 1px solid var(--border);
	}

	.logo {
		font-size: 16px;
		font-weight: 600;
		letter-spacing: -0.3px;
		margin: 0;
	}

	.header-actions {
		display: flex;
		gap: 4px;
	}

	.icon-btn {
		width: 30px;
		height: 30px;
		border-radius: 6px;
		border: none;
		background: transparent;
		color: var(--text-secondary);
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.icon-btn:hover {
		background: var(--bg-tertiary);
		color: var(--text);
	}

	.tabs {
		display: flex;
		border-bottom: 1px solid var(--border);
	}

	.tabs button {
		flex: 1;
		padding: 8px;
		border: none;
		background: none;
		font-size: 12px;
		color: var(--text-secondary);
		cursor: pointer;
		border-bottom: 2px solid transparent;
	}

	.tabs button.active {
		color: var(--text);
		border-bottom-color: var(--accent);
	}

	.list {
		flex: 1;
		overflow-y: auto;
		padding: 8px;
	}

	.item {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 8px 10px;
		border-radius: 8px;
		text-decoration: none;
		color: var(--text);
		font-size: 13px;
		transition: background 0.1s;
	}

	.item:hover {
		background: var(--bg-tertiary);
	}

	.item.active {
		background: var(--bg-tertiary);
	}

	.item-title {
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		flex: 1;
	}

	.item-meta {
		display: flex;
		align-items: center;
		gap: 6px;
		flex-shrink: 0;
		margin-left: 8px;
	}

	.type-badge {
		font-size: 9px;
		text-transform: uppercase;
		letter-spacing: 0.3px;
		font-weight: 600;
		padding: 1px 5px;
		border-radius: 3px;
		background: color-mix(in srgb, var(--type-color) 15%, transparent);
		color: var(--type-color);
	}

	.item-date {
		font-size: 11px;
		color: var(--text-secondary);
		flex-shrink: 0;
	}

	.empty {
		padding: 16px;
		text-align: center;
		font-size: 13px;
		color: var(--text-secondary);
	}
</style>
