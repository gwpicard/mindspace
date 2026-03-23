<script lang="ts">
	interface Props {
		onSend: (content: string) => void;
		disabled?: boolean;
		placeholder?: string;
	}

	let { onSend, disabled = false, placeholder = "What's on your mind?" }: Props = $props();

	let value = $state('');
	let textarea: HTMLTextAreaElement;

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			submit();
		}
	}

	function submit() {
		const text = value.trim();
		if (!text || disabled) return;
		onSend(text);
		value = '';
		// Reset textarea height
		if (textarea) textarea.style.height = 'auto';
	}

	function autoResize() {
		if (textarea) {
			textarea.style.height = 'auto';
			textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
		}
	}

	$effect(() => {
		if (textarea && !disabled) {
			textarea.focus();
		}
	});
</script>

<div class="chat-input">
	<textarea
		bind:this={textarea}
		bind:value
		onkeydown={handleKeydown}
		oninput={autoResize}
		{placeholder}
		{disabled}
		rows="1"
	></textarea>
	<button onclick={submit} disabled={disabled || !value.trim()}>
		<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
			<line x1="22" y1="2" x2="11" y2="13"></line>
			<polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
		</svg>
	</button>
</div>

<style>
	.chat-input {
		display: flex;
		gap: 8px;
		align-items: flex-end;
		padding: 12px 16px;
		border-top: 1px solid var(--border);
		background: var(--bg);
	}

	textarea {
		flex: 1;
		border: 1px solid var(--border);
		border-radius: 12px;
		padding: 10px 14px;
		font-size: 14px;
		line-height: 1.5;
		resize: none;
		background: var(--bg-secondary);
		color: var(--text);
		font-family: inherit;
		outline: none;
		transition: border-color 0.15s;
	}

	textarea:focus {
		border-color: var(--accent);
	}

	button {
		flex-shrink: 0;
		width: 38px;
		height: 38px;
		border-radius: 50%;
		border: none;
		background: var(--accent);
		color: white;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: opacity 0.15s;
	}

	button:disabled {
		opacity: 0.4;
		cursor: default;
	}

	button:not(:disabled):hover {
		opacity: 0.85;
	}
</style>
