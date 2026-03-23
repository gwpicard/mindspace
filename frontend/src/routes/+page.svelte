<script lang="ts">
	import ChatInput from '$lib/components/ChatInput.svelte';
	import { startNewConversation } from '$lib/stores/conversations';
	import { goto } from '$app/navigation';

	let sending = $state(false);

	async function handleSend(content: string) {
		sending = true;
		try {
			const conv = await startNewConversation();
			// Store the pending message to send after navigation
			sessionStorage.setItem('pendingMessage', JSON.stringify({ convId: conv.id, content }));
			goto(`/conversation/${conv.id}`);
		} catch (e) {
			console.error('Failed to create conversation:', e);
			sending = false;
		}
	}
</script>

<div class="home">
	<div class="hero">
		<h2>mindspace</h2>
		<p>What's on your mind?</p>
	</div>
	<div class="input-area">
		<ChatInput onSend={handleSend} disabled={sending} />
	</div>
</div>

<style>
	.home {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 40px;
	}

	.hero {
		text-align: center;
		margin-bottom: 40px;
	}

	.hero h2 {
		font-size: 32px;
		font-weight: 300;
		letter-spacing: -0.5px;
		margin: 0 0 8px;
	}

	.hero p {
		color: var(--text-secondary);
		font-size: 16px;
		margin: 0;
	}

	.input-area {
		width: 100%;
		max-width: 600px;
	}

	.input-area :global(.chat-input) {
		border-top: none;
	}
</style>
