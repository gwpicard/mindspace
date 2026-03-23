import { writable } from 'svelte/store';
import type { Resource } from '$lib/api';
import { listResources } from '$lib/api';

export const resources = writable<Resource[]>([]);

export async function loadResources() {
	const list = await listResources();
	resources.set(list);
}
