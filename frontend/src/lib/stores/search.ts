import { writable } from 'svelte/store';
import type { SearchResult } from '$lib/api';
import { search as apiSearch } from '$lib/api';

export const searchResults = writable<SearchResult[]>([]);
export const searchQuery = writable('');
export const searchOpen = writable(false);
export const searching = writable(false);

export async function performSearch(query: string) {
	if (!query.trim()) {
		searchResults.set([]);
		return;
	}
	searching.set(true);
	try {
		const results = await apiSearch(query);
		searchResults.set(results);
	} finally {
		searching.set(false);
	}
}
