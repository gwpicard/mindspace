<script lang="ts">
	import '../app.css';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import SearchModal from '$lib/components/SearchModal.svelte';

	let { children } = $props();
</script>

<div class="app">
	<Sidebar />
	<main class="main">
		{@render children()}
	</main>
</div>
<SearchModal />

<style>
	.app {
		display: flex;
		height: 100vh;
		overflow: hidden;
	}

	.main {
		flex: 1;
		display: flex;
		flex-direction: column;
		overflow: hidden;
	}
</style>
