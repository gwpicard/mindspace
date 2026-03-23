<script lang="ts">
	import { page } from '$app/state';
	import { onMount, tick } from 'svelte';
	import ChatInput from '$lib/components/ChatInput.svelte';
	import MessageBubble from '$lib/components/MessageBubble.svelte';
	import ResourceStatus from '$lib/components/ResourceStatus.svelte';
	import {
		currentConversation,
		loadConversation,
		appendMessage,
		updateLastAssistantMessage,
		loadConversations,
	} from '$lib/stores/conversations';
	import { channels, loadChannels } from '$lib/stores/channels';
	import { sendMessage, updateConversation, createChannel } from '$lib/api';

	let sending = $state(false);
	let messagesEl: HTMLDivElement;
	let pendingResources = $state<Array<{ id: string; url: string; type: string }>>([]);
	let duplicateResources = $state<
		Array<{ id: string; url: string; title: string | null; conversation_id: string | null }>
	>([]);
	let showChannelDropdown = $state(false);
	let newChannelName = $state('');
	let addingChannel = $state(false);

	$effect(() => {
		const id = page.params.id;
		if (id) {
			loadConversation(id);
		}
	});

	onMount(() => {
		loadChannels();
	});

	onMount(async () => {
		// Check for pending message from home page
		const pending = sessionStorage.getItem('pendingMessage');
		if (pending) {
			sessionStorage.removeItem('pendingMessage');
			try {
				const { convId, content } = JSON.parse(pending);
				if (convId === page.params.id) {
					await tick();
					handleSend(content);
				}
			} catch {
				// Ignore malformed sessionStorage data
			}
		}
	});

	async function scrollToBottom() {
		await tick();
		if (messagesEl) {
			messagesEl.scrollTop = messagesEl.scrollHeight;
		}
	}

	async function handleSend(content: string) {
		if (sending) return;
		sending = true;
		pendingResources = [];
		duplicateResources = [];

		const convId = page.params.id;

		// Optimistically add user message
		appendMessage({
			id: 'temp-user',
			role: 'user',
			content,
			created_at: new Date().toISOString(),
			cognitive_operations: null,
		});
		await scrollToBottom();

		// Add placeholder assistant message
		appendMessage({
			id: 'temp-assistant',
			role: 'assistant',
			content: '',
			created_at: new Date().toISOString(),
			cognitive_operations: null,
		});

		let fullText = '';
		try {
			for await (const event of sendMessage(convId, content)) {
				switch (event.event) {
					case 'token': {
						const { text } = event.data as { text: string };
						fullText += text;
						updateLastAssistantMessage(fullText);
						await scrollToBottom();
						break;
					}
					case 'resource_detected': {
						const res = event.data as { id: string; url: string; type: string };
						pendingResources = [...pendingResources, res];
						break;
					}
					case 'resource_duplicate': {
						const dup = event.data as {
							id: string;
							url: string;
							title: string | null;
							conversation_id: string | null;
						};
						duplicateResources = [...duplicateResources, dup];
						break;
					}
					case 'message_complete': {
						// Reload to get final state with real IDs
						await loadConversation(convId);
						await loadConversations();
						break;
					}
					case 'error': {
						const { error } = event.data as { error: string };
						updateLastAssistantMessage(`Error: ${error}`);
						break;
					}
				}
			}
		} catch (e) {
			updateLastAssistantMessage(`Error: ${e}`);
		}

		sending = false;
		await scrollToBottom();
	}

	let convChannels = $derived(
		$currentConversation && $channels.length
			? $channels.filter((ch) => $currentConversation!.channel_ids.includes(ch.id))
			: []
	);

	let availableChannels = $derived(
		$currentConversation
			? $channels.filter((ch) => !$currentConversation!.channel_ids.includes(ch.id))
			: $channels
	);

	async function toggleChannel(channelId: string) {
		const conv = $currentConversation;
		if (!conv) return;

		const current = conv.channel_ids || [];
		const newIds = current.includes(channelId)
			? current.filter((id) => id !== channelId)
			: [...current, channelId];

		await updateConversation(conv.id, { channel_ids: newIds });
		await loadConversation(conv.id);
		showChannelDropdown = false;
	}

	async function handleNewChannel() {
		const name = newChannelName.trim();
		if (!name || addingChannel) return;
		addingChannel = true;
		try {
			const ch = await createChannel(name);
			await loadChannels();
			newChannelName = '';
			await toggleChannel(ch.id);
			showChannelDropdown = false;
		} finally {
			addingChannel = false;
		}
	}
</script>

<div class="conversation">
	{#if $currentConversation}
		<header class="conv-header">
			<h2>{$currentConversation.title || 'New conversation'}</h2>
			<div class="channel-tags">
				{#each convChannels as ch (ch.id)}
					<button class="channel-tag" onclick={() => toggleChannel(ch.id)}>
						{ch.name} <span class="remove">&times;</span>
					</button>
				{/each}
				<div class="channel-add-wrapper">
					<button class="channel-add-btn" onclick={() => (showChannelDropdown = !showChannelDropdown)}>
						+ Add channel
					</button>
					{#if showChannelDropdown}
						<div class="channel-dropdown">
							{#each availableChannels as ch (ch.id)}
								<button class="channel-option" onclick={() => toggleChannel(ch.id)}>
									{ch.name}
								</button>
							{/each}
							<div class="new-channel-row">
								<input
									type="text"
									placeholder="New channel..."
									bind:value={newChannelName}
									onkeydown={(e) => e.key === 'Enter' && handleNewChannel()}
								/>
								<button onclick={handleNewChannel} disabled={!newChannelName.trim() || addingChannel}>+</button>
							</div>
						</div>
					{/if}
				</div>
			</div>
		</header>

		<div class="messages" bind:this={messagesEl}>
			{#each $currentConversation.messages as message (message.id)}
				<MessageBubble {message} />
			{/each}

			{#each pendingResources as res (res.id)}
				<ResourceStatus url={res.url} type={res.type} />
			{/each}

			{#each duplicateResources as dup (dup.id)}
				<div class="duplicate-notice">
					Previously captured: <a href="/resource/{dup.id}">{dup.title || dup.url}</a>
				</div>
			{/each}
		</div>

		<ChatInput onSend={handleSend} disabled={sending} />
	{:else}
		<div class="loading">Loading...</div>
	{/if}
</div>

<style>
	.conversation {
		flex: 1;
		display: flex;
		flex-direction: column;
		overflow: hidden;
	}

	.conv-header {
		padding: 12px 20px;
		border-bottom: 1px solid var(--border);
	}

	.conv-header h2 {
		margin: 0;
		font-size: 16px;
		font-weight: 500;
	}

	.channel-tags {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 6px;
		margin-top: 6px;
	}

	.channel-tag {
		background: var(--bg-secondary, #e8e8e8);
		border: none;
		border-radius: 12px;
		padding: 2px 10px;
		font-size: 12px;
		cursor: pointer;
		display: flex;
		align-items: center;
		gap: 4px;
		color: var(--text-primary);
	}

	.channel-tag:hover {
		background: var(--bg-tertiary, #d0d0d0);
	}

	.channel-tag .remove {
		font-size: 14px;
		opacity: 0.5;
	}

	.channel-tag:hover .remove {
		opacity: 1;
	}

	.channel-add-wrapper {
		position: relative;
	}

	.channel-add-btn {
		background: none;
		border: 1px dashed var(--border);
		border-radius: 12px;
		padding: 2px 10px;
		font-size: 12px;
		cursor: pointer;
		color: var(--text-secondary);
	}

	.channel-add-btn:hover {
		border-color: var(--text-primary);
		color: var(--text-primary);
	}

	.channel-dropdown {
		position: absolute;
		top: 100%;
		left: 0;
		margin-top: 4px;
		background: var(--bg-primary, #fff);
		border: 1px solid var(--border);
		border-radius: 8px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
		min-width: 180px;
		z-index: 10;
		overflow: hidden;
	}

	.channel-option {
		display: block;
		width: 100%;
		text-align: left;
		background: none;
		border: none;
		padding: 8px 12px;
		font-size: 13px;
		cursor: pointer;
		color: var(--text-primary);
	}

	.channel-option:hover {
		background: var(--bg-secondary, #f0f0f0);
	}

	.new-channel-row {
		display: flex;
		gap: 4px;
		padding: 6px 8px;
		border-top: 1px solid var(--border);
	}

	.new-channel-row input {
		flex: 1;
		border: 1px solid var(--border);
		border-radius: 4px;
		padding: 4px 8px;
		font-size: 12px;
		background: var(--bg-primary, #fff);
		color: var(--text-primary);
	}

	.new-channel-row button {
		background: var(--bg-secondary, #e8e8e8);
		border: none;
		border-radius: 4px;
		padding: 4px 8px;
		cursor: pointer;
		font-size: 12px;
		color: var(--text-primary);
	}

	.duplicate-notice {
		background: var(--bg-secondary, #f5f5dc);
		border-left: 3px solid var(--text-secondary, #888);
		padding: 8px 12px;
		margin: 4px 0;
		border-radius: 4px;
		font-size: 13px;
		color: var(--text-secondary);
	}

	.duplicate-notice a {
		color: var(--text-primary);
		text-decoration: underline;
	}

	.messages {
		flex: 1;
		overflow-y: auto;
		padding: 20px;
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.loading {
		flex: 1;
		display: flex;
		align-items: center;
		justify-content: center;
		color: var(--text-secondary);
	}
</style>
