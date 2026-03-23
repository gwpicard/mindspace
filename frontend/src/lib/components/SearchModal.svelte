<script lang="ts">
	import { searchOpen, searchResults, searchQuery, searching, performSearch } from '$lib/stores/search';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	const SOURCE_LABELS: Record<string, string> = {
		capture: 'Resource',
		conversation: 'Conversation',
	};

	const SOURCE_COLORS: Record<string, string> = {
		capture: '#8b5cf6',
		conversation: '#3b82f6',
	};

	let inputEl: HTMLInputElement;
	let debounceTimer: ReturnType<typeof setTimeout>;

	function close() {
		searchOpen.set(false);
		searchQuery.set('');
		searchResults.set([]);
	}

	function onInput(e: Event) {
		const val = (e.target as HTMLInputElement).value;
		searchQuery.set(val);
		clearTimeout(debounceTimer);
		debounceTimer = setTimeout(() => performSearch(val), 300);
	}

	function selectResult(result: (typeof $searchResults)[0]) {
		if (result.source === 'capture' && result.capture_id) {
			goto(`/resource/${result.capture_id}`);
		} else if (result.conversation_id) {
			goto(`/conversation/${result.conversation_id}`);
		}
		close();
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') close();
	}

	onMount(() => {
		inputEl?.focus();

		function globalKeydown(e: KeyboardEvent) {
			if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
				e.preventDefault();
				if ($searchOpen) {
					close();
				} else {
					searchOpen.set(true);
				}
			}
		}

		document.addEventListener('keydown', globalKeydown);
		return () => {
			document.removeEventListener('keydown', globalKeydown);
			clearTimeout(debounceTimer);
		};
	});
</script>

{#if $searchOpen}
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div class="overlay" data-testid="search-modal" onclick={close} onkeydown={handleKeydown}>
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<div class="modal" onclick={(e) => e.stopPropagation()} onkeydown={handleKeydown}>
			<input
				bind:this={inputEl}
				data-testid="search-input"
				type="text"
				placeholder="Search your mind..."
				value={$searchQuery}
				oninput={onInput}
				onkeydown={handleKeydown}
			/>

			{#if $searching}
				<div class="status">Searching...</div>
			{/if}

			{#if $searchResults.length > 0}
				<div class="results">
					{#each $searchResults as result}
						<button class="result" onclick={() => selectResult(result)}>
							<div class="result-header">
								<span class="result-type" style="--type-color: {SOURCE_COLORS[result.source] || '#888'}">{SOURCE_LABELS[result.source] || result.source}</span>
								{#if result.conversation_title || result.title}
									<span class="result-title">{result.conversation_title || result.title}</span>
								{/if}
							</div>
							<p class="result-snippet">{result.snippet}</p>
						</button>
					{/each}
				</div>
			{:else if $searchQuery && !$searching}
				<div class="status">No results found</div>
			{/if}
		</div>
	</div>
{/if}

<style>
	.overlay {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.5);
		display: flex;
		align-items: flex-start;
		justify-content: center;
		padding-top: 15vh;
		z-index: 100;
	}

	.modal {
		width: 560px;
		max-height: 60vh;
		background: var(--bg);
		border-radius: 12px;
		border: 1px solid var(--border);
		overflow: hidden;
		display: flex;
		flex-direction: column;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
	}

	input {
		width: 100%;
		padding: 14px 18px;
		border: none;
		border-bottom: 1px solid var(--border);
		font-size: 16px;
		background: transparent;
		color: var(--text);
		outline: none;
	}

	.results {
		overflow-y: auto;
		flex: 1;
	}

	.result {
		width: 100%;
		padding: 10px 18px;
		border: none;
		border-bottom: 1px solid var(--border);
		background: transparent;
		text-align: left;
		cursor: pointer;
		color: var(--text);
	}

	.result:hover {
		background: var(--bg-secondary);
	}

	.result-header {
		display: flex;
		align-items: center;
		gap: 8px;
		margin-bottom: 4px;
	}

	.result-type {
		font-size: 10px;
		text-transform: uppercase;
		font-weight: 600;
		letter-spacing: 0.3px;
		padding: 2px 7px;
		border-radius: 4px;
		background: color-mix(in srgb, var(--type-color) 15%, transparent);
		color: var(--type-color);
	}

	.result-title {
		font-size: 13px;
		font-weight: 500;
	}

	.result-snippet {
		font-size: 12px;
		color: var(--text-secondary);
		margin: 0;
		overflow: hidden;
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
	}

	.status {
		padding: 16px;
		text-align: center;
		font-size: 13px;
		color: var(--text-secondary);
	}
</style>
